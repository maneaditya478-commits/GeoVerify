"""Scoring engine and status evaluator for GeoVerify India."""

from typing import List, Tuple, Optional, Any
from app.config import settings
from app.schemas.verification import (
    VerificationStatus,
    ScoreBreakdown,
    EvidenceItem,
    BoundaryVerificationResult,
    PinVerificationResult
)
from app.schemas.hierarchy import AdministrativeHierarchyResult
from app.verification.decision_engine import decision_engine


class ScoringEngine:
    """Computes transparent Geographic Consistency Score and derives status."""

    @classmethod
    def calculate_score(
        cls,
        evidence_items: List[EvidenceItem],
        hierarchy: AdministrativeHierarchyResult,
        boundary: BoundaryVerificationResult,
        pin: PinVerificationResult,
        is_ambiguous: bool = False,
        top_candidate: Optional[Any] = None,
        ambiguity_details: Optional[Any] = None
    ) -> Tuple[int, ScoreBreakdown, VerificationStatus, str]:
        weights = settings.scoring_weights

        hierarchy_score = sum(i.score_contribution for i in evidence_items if i.category == "hierarchy")
        boundary_score = sum(i.score_contribution for i in evidence_items if i.category == "boundary")
        locality_score = sum(i.score_contribution for i in evidence_items if i.category == "locality")
        pincode_score = sum(i.score_contribution for i in evidence_items if i.category == "pincode")
        geocoding_score = sum(i.score_contribution for i in evidence_items if i.category == "geocoding")
        nearby_score = sum(i.score_contribution for i in evidence_items if i.category == "nearby")

        total_score_raw = (
            hierarchy_score +
            boundary_score +
            locality_score +
            pincode_score +
            geocoding_score +
            nearby_score
        )
        total_score = max(0, min(100, int(round(total_score_raw))))

        score_breakdown = ScoreBreakdown(
            hierarchy_score=round(hierarchy_score, 1),
            hierarchy_max=float(weights["hierarchy"]),
            boundary_score=round(boundary_score, 1),
            boundary_max=float(weights["boundary"]),
            locality_score=round(locality_score, 1),
            locality_max=float(weights["locality"]),
            pincode_score=round(pincode_score, 1),
            pincode_max=float(weights["pincode"]),
            geocoding_score=round(geocoding_score, 1),
            geocoding_max=float(weights["geocoding"]),
            nearby_score=round(nearby_score, 1),
            nearby_max=float(weights["nearby"]),
            total_score=total_score
        )

        # Evaluate verification decision via VerificationDecisionEngine
        decision = decision_engine.evaluate(
            consistency_score=total_score,
            hierarchy=hierarchy,
            boundary=boundary,
            pin=pin,
            is_ambiguous=is_ambiguous,
            top_candidate=top_candidate,
            ambiguity_details=ambiguity_details
        )

        return total_score, score_breakdown, decision.status, decision.summary
