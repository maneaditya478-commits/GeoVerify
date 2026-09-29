"""End-to-end Address Entity Resolver, Candidate Re-Ranker, and Completeness Evaluator."""

from typing import Optional, Dict, Any, List, Set
from app.entity_resolution.models import (
    CandidateEntity,
    EntityMatchResult,
    ResolutionResult,
    AmbiguityDetails,
    CompletenessCriteria,
    CompletenessBreakdown,
    CompletenessResult,
    EntityType
)
from app.entity_resolution.candidates import candidate_generator
from app.entity_resolution.matcher import entity_matcher
from app.entity_resolution.ambiguity import ambiguity_detector
from app.schemas.address import ParsedAddress, Coordinates
from app.services.address_parser import AddressParser
from app.services.transliteration import transliteration_service


class AddressEntityResolver:
    """Orchestrates multi-strategy candidate generation, context-aware re-ranking, ambiguity detection, and completeness scoring."""

    # Completeness weights (Total 100 points)
    COMPLETENESS_WEIGHT_STATE = 20.0
    COMPLETENESS_WEIGHT_DISTRICT = 25.0
    COMPLETENESS_WEIGHT_LOCALITY = 25.0
    COMPLETENESS_WEIGHT_PINCODE = 15.0
    COMPLETENESS_WEIGHT_SUBDISTRICT = 5.0
    COMPLETENESS_WEIGHT_PREMISE = 5.0
    COMPLETENESS_WEIGHT_LANDMARK = 5.0

    @classmethod
    def calculate_completeness(cls, parsed: ParsedAddress) -> CompletenessResult:
        """
        Evaluates whether the address contains enough information for reliable geographic resolution.
        Does NOT unfairly penalize missing house numbers if geographic administrative hierarchy is present.
        """
        has_state = bool(parsed.state)
        has_district = bool(parsed.district or parsed.city)
        has_subdistrict = bool(parsed.subdistrict)
        has_locality = bool(parsed.locality)
        has_pincode = bool(parsed.pincode)
        has_premise = bool(parsed.premise)
        has_landmark = bool(parsed.landmarks and len(parsed.landmarks) > 0)

        criteria = CompletenessCriteria(
            has_state=has_state,
            has_district=has_district,
            has_subdistrict=has_subdistrict,
            has_locality=has_locality,
            has_pincode=has_pincode,
            has_premise=has_premise,
            has_landmark=has_landmark
        )

        state_pts = cls.COMPLETENESS_WEIGHT_STATE if has_state else 0.0
        dist_pts = cls.COMPLETENESS_WEIGHT_DISTRICT if has_district else 0.0
        subdist_pts = cls.COMPLETENESS_WEIGHT_SUBDISTRICT if has_subdistrict else 0.0
        loc_pts = cls.COMPLETENESS_WEIGHT_LOCALITY if has_locality else 0.0
        pin_pts = cls.COMPLETENESS_WEIGHT_PINCODE if has_pincode else 0.0
        prem_pts = cls.COMPLETENESS_WEIGHT_PREMISE if has_premise else 0.0
        land_pts = cls.COMPLETENESS_WEIGHT_LANDMARK if has_landmark else 0.0

        total = round(state_pts + dist_pts + subdist_pts + loc_pts + pin_pts + prem_pts + land_pts)
        score = min(100, max(0, total))

        missing = []
        if not has_locality: missing.append("Locality / Village / Area")
        if not has_district: missing.append("District / City")
        if not has_state: missing.append("State")
        if not has_pincode: missing.append("PIN Code")
        if not has_subdistrict: missing.append("Sub-district / Taluka (Optional)")

        rating = "COMPLETE" if score >= 85 else ("ADEQUATE" if score >= 65 else ("PARTIAL" if score >= 40 else "MINIMAL"))

        breakdown = CompletenessBreakdown(
            state_points=state_pts,
            district_points=dist_pts,
            subdistrict_points=subdist_pts,
            locality_points=loc_pts,
            pincode_points=pin_pts,
            premise_points=prem_pts,
            landmark_points=land_pts,
            total_score=float(score)
        )

        return CompletenessResult(
            score=score,
            rating=rating,
            criteria=criteria,
            breakdown=breakdown,
            missing_fields=missing
        )

    @classmethod
    def resolve_address(
        cls,
        address_text: str,
        parsed_override: Optional[ParsedAddress] = None,
        context_coordinates: Optional[Coordinates] = None
    ) -> ResolutionResult:
        """
        Resolves an address string into structured entities, ranked candidate matches,
        ambiguity status, and completeness score using multi-stage candidate retrieval.
        """
        parsed = parsed_override or AddressParser.parse(address_text)
        script = transliteration_service.detect_script(address_text)

        resolved_entities: Dict[str, Optional[CandidateEntity]] = {
            "state": None,
            "district": None,
            "subdistrict": None,
            "locality": None,
            "pincode": None
        }

        all_candidate_matches: List[EntityMatchResult] = []

        # 1. State Candidate Resolution
        if parsed.state:
            state_candidates = candidate_generator.generate_candidates(
                parsed.state, expected_type=EntityType.STATE, limit=3
            )
            for c in state_candidates:
                match_res = entity_matcher.match_candidate(
                    c, query_text=parsed.state, context_state=parsed.state
                )
                all_candidate_matches.append(match_res)
                if not resolved_entities["state"] and match_res.match_score >= 70.0:
                    resolved_entities["state"] = c

        # 2. District Candidate Resolution
        target_dist = parsed.district or parsed.city
        if target_dist:
            dist_candidates = candidate_generator.generate_candidates(
                target_dist,
                expected_type=EntityType.DISTRICT,
                context_state=parsed.state or (resolved_entities["state"].name if resolved_entities["state"] else None),
                limit=5
            )
            for c in dist_candidates:
                match_res = entity_matcher.match_candidate(
                    c, query_text=target_dist, context_state=parsed.state, context_district=target_dist
                )
                all_candidate_matches.append(match_res)
                if not resolved_entities["district"] and match_res.match_score >= 70.0:
                    resolved_entities["district"] = c

        # 3. Sub-District Candidate Resolution
        if parsed.subdistrict:
            sd_candidates = candidate_generator.generate_candidates(
                parsed.subdistrict,
                expected_type=EntityType.SUBDISTRICT,
                context_state=parsed.state,
                context_district=target_dist,
                limit=5
            )
            for c in sd_candidates:
                match_res = entity_matcher.match_candidate(
                    c, query_text=parsed.subdistrict, context_state=parsed.state,
                    context_district=target_dist, context_subdistrict=parsed.subdistrict
                )
                all_candidate_matches.append(match_res)
                if not resolved_entities["subdistrict"] and match_res.match_score >= 65.0:
                    resolved_entities["subdistrict"] = c

        # 4. Locality Candidate Resolution & Multi-Token Expansion
        locality_matches: List[EntityMatchResult] = []
        loc_queries: List[str] = []
        if parsed.locality:
            loc_queries.append(parsed.locality)
        for lm in (parsed.landmarks or []):
            if lm and lm not in loc_queries:
                loc_queries.append(lm)
        for tok in (parsed.unparsed_tokens or []):
            if tok and len(tok) >= 3 and tok not in loc_queries:
                loc_queries.append(tok)

        seen_loc_candidate_ids: Set[str] = set()

        for q in loc_queries:
            loc_cands = candidate_generator.generate_candidates(
                q,
                expected_type=EntityType.LOCALITY,
                context_state=parsed.state or (resolved_entities["state"].name if resolved_entities["state"] else None),
                context_district=target_dist or (resolved_entities["district"].name if resolved_entities["district"] else None),
                context_subdistrict=parsed.subdistrict,
                context_pin=parsed.pincode,
                context_coordinates=context_coordinates,
                limit=8
            )
            for c in loc_cands:
                if c.id in seen_loc_candidate_ids:
                    continue
                seen_loc_candidate_ids.add(c.id)

                match_res = entity_matcher.match_candidate(
                    c,
                    query_text=q,
                    context_state=parsed.state,
                    context_district=target_dist,
                    context_subdistrict=parsed.subdistrict,
                    context_pin=parsed.pincode,
                    context_coordinates=context_coordinates
                )
                locality_matches.append(match_res)
                all_candidate_matches.append(match_res)

        # Sort locality candidates by match score
        locality_matches.sort(key=lambda m: m.match_score, reverse=True)
        if locality_matches and locality_matches[0].match_score >= 60.0:
            resolved_entities["locality"] = locality_matches[0].candidate

        # 5. PIN Code Candidate Resolution
        if parsed.pincode:
            pin_candidates = candidate_generator.generate_candidates(
                parsed.pincode, expected_type=EntityType.PINCODE, limit=2
            )
            for c in pin_candidates:
                match_res = entity_matcher.match_candidate(
                    c, query_text=parsed.pincode, context_state=parsed.state, context_district=target_dist, context_pin=parsed.pincode
                )
                all_candidate_matches.append(match_res)
                if not resolved_entities["pincode"]:
                    resolved_entities["pincode"] = c

        # Sort all candidates by match score descending
        all_candidate_matches.sort(key=lambda m: m.match_score, reverse=True)

        # Check Ambiguity on locality candidates or top matches
        ambiguity_res = ambiguity_detector.detect_ambiguity(
            locality_matches if locality_matches else all_candidate_matches
        )

        # Completeness calculation
        completeness_res = cls.calculate_completeness(parsed)

        # Compute overall Entity Match Score
        entity_score = 0
        if all_candidate_matches:
            top_scores = [m.match_score for m in all_candidate_matches[:3]]
            entity_score = round(sum(top_scores) / len(top_scores))

        return ResolutionResult(
            query_text=address_text,
            detected_script=script,
            resolved_entities=resolved_entities,
            candidate_matches=all_candidate_matches[:10],
            ambiguity=ambiguity_res,
            completeness=completeness_res,
            entity_match_score=entity_score
        )


address_entity_resolver = AddressEntityResolver()
