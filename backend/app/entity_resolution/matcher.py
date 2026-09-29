"""Transparent multi-factor Entity Match Scorer for geographic candidate ranking."""

from typing import Optional, List, Tuple
import math
from app.entity_resolution.models import (
    CandidateEntity,
    EntityMatchResult,
    EntityMatchBreakdown,
    EntityType
)
from app.schemas.address import Coordinates
from app.entity_resolution.ranking import context_aware_ranker, ContextAwareRanker


def _haversine_distance(c1: Coordinates, c2: Coordinates) -> float:
    """Computes great-circle distance between two geographic coordinates in kilometers."""
    R = 6371.0
    lat1_rad = math.radians(c1.latitude)
    lat2_rad = math.radians(c2.latitude)
    dlat = math.radians(c2.latitude - c1.latitude)
    dlon = math.radians(c2.longitude - c1.longitude)
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


class EntityMatcher:
    """Computes transparent Entity Match Scores (0-100) combining textual, hierarchical, and spatial signals."""

    WEIGHT_NAME_SIMILARITY: float = 40.0
    WEIGHT_ADMIN_CONTEXT: float = 25.0
    WEIGHT_PIN_COMPATIBILITY: float = 15.0
    WEIGHT_GEOGRAPHIC_PROXIMITY: float = 15.0
    WEIGHT_ENTITY_TYPE: float = 5.0

    @classmethod
    def match_candidate(
        cls,
        candidate: CandidateEntity,
        query_text: str,
        context_state: Optional[str] = None,
        context_district: Optional[str] = None,
        context_subdistrict: Optional[str] = None,
        context_pin: Optional[str] = None,
        context_coordinates: Optional[Coordinates] = None,
        expected_type: Optional[EntityType] = None
    ) -> EntityMatchResult:
        """Evaluates a candidate entity against the provided contextual signals."""
        
        # 1. Name similarity (0 - 40 points)
        name_sim_points = round(candidate.similarity_score * cls.WEIGHT_NAME_SIMILARITY, 2)

        # 2. Administrative context agreement (0 - 25 points)
        admin_points = 0.0
        admin_factors = 0
        admin_matches = 0

        if context_state:
            admin_factors += 1
            if candidate.state and (context_state.lower() in candidate.state.lower() or candidate.state.lower() in context_state.lower()):
                admin_matches += 1

        if context_district:
            admin_factors += 1
            if candidate.district and (context_district.lower() in candidate.district.lower() or candidate.district.lower() in context_district.lower()):
                admin_matches += 1

        if context_subdistrict and candidate.subdistrict:
            admin_factors += 1
            if context_subdistrict.lower() in candidate.subdistrict.lower() or candidate.subdistrict.lower() in context_subdistrict.lower():
                admin_matches += 1

        if admin_factors > 0:
            admin_points = round((admin_matches / admin_factors) * cls.WEIGHT_ADMIN_CONTEXT, 2)
        else:
            # Neutral default if no context was provided
            admin_points = round(cls.WEIGHT_ADMIN_CONTEXT * 0.5, 2)

        # 3. PIN compatibility (0 - 15 points)
        pin_points = 0.0
        if context_pin and candidate.pincode:
            if context_pin == candidate.pincode:
                pin_points = cls.WEIGHT_PIN_COMPATIBILITY
            elif context_pin[:3] == candidate.pincode[:3]:
                pin_points = round(cls.WEIGHT_PIN_COMPATIBILITY * 0.7, 2)
            elif context_pin[0] == candidate.pincode[0]:
                pin_points = round(cls.WEIGHT_PIN_COMPATIBILITY * 0.4, 2)
        elif not context_pin:
            pin_points = round(cls.WEIGHT_PIN_COMPATIBILITY * 0.5, 2)

        # 4. Geographic proximity (0 - 15 points)
        prox_points = 0.0
        if context_coordinates and candidate.coordinates:
            dist_km = _haversine_distance(context_coordinates, candidate.coordinates)
            if dist_km <= 5.0:
                prox_points = cls.WEIGHT_GEOGRAPHIC_PROXIMITY
            elif dist_km <= 15.0:
                prox_points = round(cls.WEIGHT_GEOGRAPHIC_PROXIMITY * 0.8, 2)
            elif dist_km <= 50.0:
                prox_points = round(cls.WEIGHT_GEOGRAPHIC_PROXIMITY * 0.4, 2)
            else:
                prox_points = 0.0
        elif not context_coordinates:
            prox_points = round(cls.WEIGHT_GEOGRAPHIC_PROXIMITY * 0.5, 2)

        # 5. Entity type weight (0 - 5 points)
        type_points = cls.WEIGHT_ENTITY_TYPE if (not expected_type or candidate.entity_type == expected_type) else round(cls.WEIGHT_ENTITY_TYPE * 0.5, 2)

        # Total Entity Match Score (0 - 100)
        total_score = min(100.0, max(0.0, round(name_sim_points + admin_points + pin_points + prox_points + type_points, 1)))

        confidence = "HIGH" if total_score >= 80.0 else ("MEDIUM" if total_score >= 55.0 else "LOW")

        breakdown = EntityMatchBreakdown(
            name_similarity=name_sim_points,
            admin_context=admin_points,
            pin_compatibility=pin_points,
            geographic_proximity=prox_points,
            entity_type_weight=type_points,
            total_score=total_score
        )

        return EntityMatchResult(
            candidate=candidate,
            match_score=total_score,
            breakdown=breakdown,
            match_confidence=confidence
        )

    @classmethod
    def rank_candidates(
        cls,
        candidates: List[CandidateEntity],
        query_text: str,
        context_state: Optional[str] = None,
        context_district: Optional[str] = None,
        context_subdistrict: Optional[str] = None,
        context_pin: Optional[str] = None,
        context_coordinates: Optional[Coordinates] = None,
        expected_type: Optional[EntityType] = None
    ) -> List[EntityMatchResult]:
        """Ranks candidate entities with Phase 6 ContextAwareRanker."""
        return context_aware_ranker.rank_candidates(
            candidates=candidates,
            query_text=query_text,
            context_state=context_state,
            context_district=context_district,
            context_subdistrict=context_subdistrict,
            context_pin=context_pin,
            context_coordinates=context_coordinates,
            expected_type=expected_type
        )


entity_matcher = EntityMatcher()
