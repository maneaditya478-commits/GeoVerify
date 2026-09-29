"""Context-Aware Candidate Ranking Engine for GeoVerify India (Phase 6).

Implements multi-factor ranking with hierarchical parent-child compatibility,
explicit administrative conflict penalties, retrieval consensus bonuses,
and explainable ranking rationales.
"""

import math
import re
from typing import List, Dict, Any, Optional, Tuple, Set
from rapidfuzz import fuzz
from app.entity_resolution.models import (
    CandidateEntity,
    EntityMatchResult,
    EntityMatchBreakdown,
    EntityType,
    RankingExplanation,
    AppliedPenalty
)
from app.entity_resolution.ranking_config import (
    Phase6RankingConfig,
    default_ranking_config
)
from app.schemas.address import Coordinates
from app.verification.hierarchy import hierarchy_validator
from app.services.phonetic import phonetic_service
from app.services.transliteration import transliteration_service


def _haversine_km(c1: Coordinates, c2: Coordinates) -> float:
    """Computes great-circle distance between two coordinates in km."""
    R = 6371.0
    lat1, lat2 = math.radians(c1.latitude), math.radians(c2.latitude)
    dlat = math.radians(c2.latitude - c1.latitude)
    dlon = math.radians(c2.longitude - c1.longitude)
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


class ContextAwareRanker:
    """Multi-factor Context-Aware Candidate Ranker for Indian Geographic Entities."""

    def __init__(self, config: Optional[Phase6RankingConfig] = None):
        self.config = config or default_ranking_config

    def score_candidate(
        self,
        candidate: CandidateEntity,
        query_text: str,
        context_state: Optional[str] = None,
        context_district: Optional[str] = None,
        context_subdistrict: Optional[str] = None,
        context_pin: Optional[str] = None,
        context_coordinates: Optional[Coordinates] = None,
        expected_type: Optional[EntityType] = None,
        all_channels: Optional[List[str]] = None
    ) -> EntityMatchResult:
        """
        Computes transparent multi-factor score and applied penalties for a single candidate.
        """
        w = self.config.weights
        p = self.config.penalties

        applied_penalties: List[AppliedPenalty] = []
        admin_differences: List[str] = []

        # 1. Name Similarity (25% -> 25 points max)
        name_sim = candidate.similarity_score
        if query_text and len(query_text.strip()) >= 2:
            q_clean = query_text.strip().lower()
            query_tokens = [q_clean] + [t.strip().lower() for t in re.split(r"[,/ ]+", query_text) if len(t.strip()) >= 2]
            cand_names = [candidate.name.lower()]
            if candidate.name_hi:
                cand_names.append(candidate.name_hi.lower())
            if candidate.name_mr:
                cand_names.append(candidate.name_mr.lower())
            
            best_text_sim = 0.0
            for q_tok in query_tokens:
                sim_tok = max(fuzz.ratio(q_tok, n) / 100.0 for n in cand_names)
                if sim_tok > best_text_sim:
                    best_text_sim = sim_tok

            if candidate.match_source in ["exact", "alias", "transliteration", "phonetic", "fuzzy"]:
                name_sim = max(name_sim, best_text_sim)
            else:
                name_sim = best_text_sim
        name_pts = round(name_sim * (w.name_similarity * 100), 2)

        # 2. Administrative Context Agreement (25% -> 25 points max)
        admin_factors = 0
        admin_matches = 0
        state_conflict = False
        district_conflict = False
        subdistrict_conflict = False

        if context_state:
            admin_factors += 1
            if candidate.state and (
                context_state.lower() in candidate.state.lower() or
                candidate.state.lower() in context_state.lower() or
                (candidate.state_code and candidate.state_code.lower() == context_state.lower())
            ):
                admin_matches += 1
            elif candidate.state:
                state_conflict = True
                admin_differences.append(f"Candidate state '{candidate.state}' contradicts query state '{context_state}'")

        if context_district:
            admin_factors += 1
            if candidate.district and (
                context_district.lower() in candidate.district.lower() or
                candidate.district.lower() in context_district.lower()
            ):
                admin_matches += 1
            elif candidate.district:
                district_conflict = True
                admin_differences.append(f"Candidate district '{candidate.district}' contradicts query district '{context_district}'")

        if context_subdistrict:
            admin_factors += 1
            if candidate.subdistrict and (
                context_subdistrict.lower() in candidate.subdistrict.lower() or
                candidate.subdistrict.lower() in context_subdistrict.lower()
            ):
                admin_matches += 1
            elif candidate.subdistrict:
                subdistrict_conflict = True
                admin_differences.append(f"Candidate subdistrict '{candidate.subdistrict}' contradicts query taluka '{context_subdistrict}'")

        if admin_factors > 0:
            admin_pts = round((admin_matches / admin_factors) * (w.admin_context * 100), 2)
        else:
            admin_pts = round((w.admin_context * 100) * 0.5, 2)

        # 3. Parent-Child Hierarchical Compatibility (15% -> 15 points max)
        parent_child_pts = 0.0
        if candidate.state and candidate.district:
            # Check authoritative parent-child relationship via hierarchy validator
            h_res = hierarchy_validator.validate_hierarchy(state=candidate.state, district=candidate.district)
            if h_res.is_consistent:
                parent_child_pts = w.parent_child_compatibility * 100
            else:
                parent_child_pts = (w.parent_child_compatibility * 100) * 0.3
        elif candidate.state or candidate.district:
            parent_child_pts = (w.parent_child_compatibility * 100) * 0.7
        else:
            parent_child_pts = (w.parent_child_compatibility * 100) * 0.5
        parent_child_pts = round(parent_child_pts, 2)

        # 4. PIN Code Compatibility (10% -> 10 points max)
        pin_pts = 0.0
        pin_circle_conflict = False
        if context_pin and candidate.pincode:
            if context_pin == candidate.pincode:
                pin_pts = w.pin_compatibility * 100
            elif context_pin[:3] == candidate.pincode[:3]:
                pin_pts = round((w.pin_compatibility * 100) * 0.7, 2)
            elif context_pin[0] == candidate.pincode[0]:
                pin_pts = round((w.pin_compatibility * 100) * 0.4, 2)
            else:
                pin_pts = 0.0
                pin_circle_conflict = True
                admin_differences.append(f"Candidate PIN '{candidate.pincode}' circle contradicts query PIN '{context_pin}'")
        elif context_pin:
            pin_pts = 0.0
        else:
            pin_pts = round((w.pin_compatibility * 100) * 0.5, 2)

        # 5. Geographic Proximity / Spatial Compatibility (10% -> 10 points max)
        geo_pts = 0.0
        if context_coordinates and candidate.coordinates:
            dist_km = _haversine_km(context_coordinates, candidate.coordinates)
            if dist_km <= 5.0:
                geo_pts = w.geographic_compatibility * 100
            elif dist_km <= 15.0:
                geo_pts = round((w.geographic_compatibility * 100) * 0.8, 2)
            elif dist_km <= 50.0:
                geo_pts = round((w.geographic_compatibility * 100) * 0.4, 2)
            else:
                geo_pts = 0.0
        elif not context_coordinates:
            geo_pts = round((w.geographic_compatibility * 100) * 0.5, 2)

        # 6. Transliteration & Indic Phonetic Agreement (5% -> 5 points max)
        phonetic_pts = 0.0
        source_is_translit_phonetic = ("transliteration" in candidate.match_source or "phonetic" in candidate.match_source)
        is_devanagari = transliteration_service.detect_script(query_text) in ["Devanagari", "Hindi", "Marathi"]
        if source_is_translit_phonetic or is_devanagari:
            phonetic_pts = w.transliteration_phonetic * 100
        else:
            phonetic_pts = round((w.transliteration_phonetic * 100) * 0.6, 2)

        # 7. Entity Type Compatibility (5% -> 5 points max)
        type_pts = 0.0
        type_mismatch = False
        locality_types = {EntityType.LOCALITY, EntityType.VILLAGE, EntityType.TOWN, EntityType.CITY, EntityType.POI}
        if expected_type:
            if candidate.entity_type == expected_type:
                type_pts = w.entity_type_compatibility * 100
            elif expected_type == EntityType.LOCALITY and candidate.entity_type in locality_types:
                type_pts = round((w.entity_type_compatibility * 100) * 0.9, 2)
            elif expected_type == EntityType.LOCALITY and candidate.entity_type not in locality_types:
                type_pts = 0.0
                type_mismatch = True
                admin_differences.append(f"Entity type mismatch: expected Locality, candidate is {candidate.entity_type.value.title()}")
            elif candidate.entity_type != expected_type:
                type_pts = 0.0
                type_mismatch = True
                admin_differences.append(f"Entity type mismatch: expected {expected_type.value.title()}, candidate is {candidate.entity_type.value.title()}")
            else:
                type_pts = round((w.entity_type_compatibility * 100) * 0.5, 2)
        else:
            type_pts = round((w.entity_type_compatibility * 100) * 0.8, 2)

        # 8. Retrieval Consensus Bonus (3% -> 3 points max)
        channel_list = candidate.channels or ([candidate.match_source] if candidate.match_source else [])
        consensus_count = len(channel_list)
        if consensus_count >= 3:
            consensus_pts = w.retrieval_consensus * 100
        elif consensus_count == 2:
            consensus_pts = round((w.retrieval_consensus * 100) * 0.67, 2)
        else:
            consensus_pts = round((w.retrieval_consensus * 100) * 0.33, 2)

        # 9. Data Quality & Source Authority (2% -> 2 points max)
        quality_pts = 0.0
        if candidate.coordinates and candidate.bbox:
            quality_pts = w.data_quality * 100
        elif candidate.coordinates or candidate.bbox:
            quality_pts = round((w.data_quality * 100) * 0.7, 2)
        else:
            quality_pts = round((w.data_quality * 100) * 0.4, 2)

        # ---------------- Apply Explicit Penalties ----------------
        penalty_sum = 0.0

        if state_conflict:
            ded = p.state_conflict
            penalty_sum += ded
            applied_penalties.append(AppliedPenalty(
                name="STATE_CONFLICT",
                deduction=ded,
                reason=f"Candidate state '{candidate.state}' contradicts asserted state '{context_state}'."
            ))

        if district_conflict:
            ded = p.district_conflict
            penalty_sum += ded
            applied_penalties.append(AppliedPenalty(
                name="DISTRICT_CONFLICT",
                deduction=ded,
                reason=f"Candidate district '{candidate.district}' contradicts asserted district '{context_district}'."
            ))

        if subdistrict_conflict:
            ded = p.subdistrict_conflict
            penalty_sum += ded
            applied_penalties.append(AppliedPenalty(
                name="SUBDISTRICT_CONFLICT",
                deduction=ded,
                reason=f"Candidate subdistrict '{candidate.subdistrict}' contradicts asserted taluka '{context_subdistrict}'."
            ))

        if query_text and len(query_text.strip()) >= 2 and name_sim < 0.40:
            ded = -25.0
            penalty_sum += ded
            applied_penalties.append(AppliedPenalty(
                name="LOW_NAME_SIMILARITY",
                deduction=ded,
                reason=f"Candidate name '{candidate.name}' has low lexical similarity ({round(name_sim*100, 1)}%) to query token '{query_text}'."
            ))

        if type_mismatch:
            ded = p.entity_type_mismatch
            penalty_sum += ded
            applied_penalties.append(AppliedPenalty(
                name="ENTITY_TYPE_MISMATCH",
                deduction=ded,
                reason=f"Candidate is a {candidate.entity_type.value.title()} when target entity is a Locality."
            ))

        if pin_circle_conflict:
            ded = p.pin_circle_conflict
            penalty_sum += ded
            applied_penalties.append(AppliedPenalty(
                name="PIN_CIRCLE_CONFLICT",
                deduction=ded,
                reason=f"Candidate PIN '{candidate.pincode}' postal circle does not match queried PIN '{context_pin}'."
            ))

        # Raw total before penalties
        raw_positive_score = (
            name_pts +
            admin_pts +
            parent_child_pts +
            pin_pts +
            geo_pts +
            phonetic_pts +
            type_pts +
            consensus_pts +
            quality_pts
        )

        final_score = max(0.0, min(100.0, round(raw_positive_score + penalty_sum, 1)))

        # Confidence categorization
        if final_score >= self.config.confidence.high_threshold:
            confidence = "HIGH"
        elif final_score >= self.config.confidence.medium_threshold:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        breakdown = EntityMatchBreakdown(
            name_similarity=name_pts,
            admin_context=admin_pts,
            parent_child_compatibility=parent_child_pts,
            pin_compatibility=pin_pts,
            geographic_proximity=geo_pts,
            transliteration_phonetic=phonetic_pts,
            entity_type_weight=type_pts,
            retrieval_consensus=consensus_pts,
            data_quality=quality_pts,
            penalty_deduction=penalty_sum,
            total_score=final_score
        )

        feature_contributions = {
            "name_similarity": name_pts,
            "admin_context": admin_pts,
            "parent_child_compatibility": parent_child_pts,
            "pin_compatibility": pin_pts,
            "geographic_proximity": geo_pts,
            "transliteration_phonetic": phonetic_pts,
            "entity_type_weight": type_pts,
            "retrieval_consensus": consensus_pts,
            "data_quality": quality_pts,
            "penalty_deduction": penalty_sum
        }

        explanation = RankingExplanation(
            feature_contributions=feature_contributions,
            applied_penalties=applied_penalties,
            total_penalty_deduction=penalty_sum,
            retrieval_channels=channel_list,
            consensus_count=consensus_count,
            admin_differences=admin_differences,
            summary=f"Scored {final_score}/100 with {len(applied_penalties)} penalty deductions."
        )

        return EntityMatchResult(
            candidate=candidate,
            match_score=final_score,
            breakdown=breakdown,
            match_confidence=confidence,
            ranking_explanation=explanation
        )

    def rank_candidates(
        self,
        candidates: List[CandidateEntity],
        query_text: str,
        context_state: Optional[str] = None,
        context_district: Optional[str] = None,
        context_subdistrict: Optional[str] = None,
        context_pin: Optional[str] = None,
        context_coordinates: Optional[Coordinates] = None,
        expected_type: Optional[EntityType] = None
    ) -> List[EntityMatchResult]:
        """
        Scores, re-ranks, and enriches candidates with rank position, score deltas, and Top-K explanations.
        """
        results: List[EntityMatchResult] = []
        for c in candidates:
            match_res = self.score_candidate(
                candidate=c,
                query_text=query_text,
                context_state=context_state,
                context_district=context_district,
                context_subdistrict=context_subdistrict,
                context_pin=context_pin,
                context_coordinates=context_coordinates,
                expected_type=expected_type
            )
            results.append(match_res)

        # Sort descending by match_score, then name similarity, then consensus
        results.sort(
            key=lambda r: (
                r.match_score,
                r.breakdown.name_similarity,
                r.breakdown.retrieval_consensus
            ),
            reverse=True
        )

        # Populate rank positions, score deltas, and summaries
        for idx, r in enumerate(results):
            rank = idx + 1
            delta = None
            if idx + 1 < len(results):
                delta = round(r.match_score - results[idx + 1].match_score, 1)

            if r.ranking_explanation:
                r.ranking_explanation.rank = rank
                r.ranking_explanation.score_delta_to_next = delta
                if delta is not None:
                    r.ranking_explanation.summary = (
                        f"Rank #{rank} ({r.match_score}/100). "
                        f"Lead over Rank #{rank+1}: +{delta} pts. "
                        f"Found via {r.ranking_explanation.consensus_count} channel(s)."
                    )
                else:
                    r.ranking_explanation.summary = (
                        f"Rank #{rank} ({r.match_score}/100). "
                        f"Found via {r.ranking_explanation.consensus_count} channel(s)."
                    )

        return results


context_aware_ranker = ContextAwareRanker()
ContextAwareCandidateRanker = ContextAwareRanker
