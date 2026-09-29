"""Deterministic Verification Decision Engine for GeoVerify India (Phase 6).

Consumes multi-signal evidence, administrative hierarchy checks, geometric point-in-polygon
evaluations, postal circle verifications, entity resolution rankings, and ambiguity metrics
to produce calibrated, deterministic verification decisions with transparent rationales.
"""

from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field

from app.schemas.verification import (
    VerificationStatus,
    ScoreBreakdown,
    EvidenceItem,
    BoundaryVerificationResult,
    PinVerificationResult
)
from app.schemas.hierarchy import AdministrativeHierarchyResult
from app.entity_resolution.models import EntityMatchResult, AmbiguityDetails


class VerificationDecision(BaseModel):
    """Detailed output of the deterministic verification decision engine."""
    status: VerificationStatus
    summary: str
    decision_rationale: List[str] = Field(default_factory=list)
    contributing_factors: Dict[str, Any] = Field(default_factory=dict)
    confidence_level: str = "HIGH"  # HIGH, MEDIUM, LOW


class VerificationDecisionEngine:
    """Evaluates multi-source evidence and derives calibrated verification statuses."""

    @classmethod
    def evaluate(
        cls,
        consistency_score: int,
        hierarchy: AdministrativeHierarchyResult,
        boundary: BoundaryVerificationResult,
        pin: PinVerificationResult,
        is_ambiguous: bool = False,
        top_candidate: Optional[EntityMatchResult] = None,
        ambiguity_details: Optional[AmbiguityDetails] = None
    ) -> VerificationDecision:
        """
        Determines the final verification status using a deterministic decision rule matrix.
        """
        rationale: List[str] = []
        factors: Dict[str, Any] = {
            "consistency_score": consistency_score,
            "hierarchy_consistent": hierarchy.is_consistent,
            "boundary_inside_district": boundary.point_inside_district,
            "pin_matched": pin.matched if pin.pincode else None,
            "is_ambiguous": is_ambiguous
        }

        # Check for administrative & geometric conflicts
        has_hierarchy_mismatch = (
            not hierarchy.is_consistent or len(hierarchy.mismatch_details) > 0
        ) and bool(hierarchy.state or hierarchy.district or hierarchy.locality)

        has_boundary_mismatch = (
            boundary.point_inside_district is False and boundary.detected_district is not None
        )

        has_pin_mismatch = (
            pin.pincode is not None and pin.is_valid_format and not pin.matched
        )

        # Rule 1: Insufficient Geographic Anchors -> UNABLE_TO_VERIFY
        if not hierarchy.state and not hierarchy.district and not hierarchy.locality and (not pin.pincode or not pin.matched):
            rationale.append("No authoritative administrative, postal, or locality tokens were found in the input address.")
            return VerificationDecision(
                status=VerificationStatus.UNABLE_TO_VERIFY,
                summary="Insufficient geographic details to verify the address.",
                decision_rationale=rationale,
                contributing_factors=factors,
                confidence_level="LOW"
            )

        # Rule 2: Administrative or Spatial Contradiction -> INCONSISTENT
        if has_hierarchy_mismatch or has_boundary_mismatch:
            if has_hierarchy_mismatch:
                rationale.append(f"Administrative hierarchy conflict: {', '.join(hierarchy.mismatch_details) if hierarchy.mismatch_details else 'Hierarchy relationship violates LGD boundaries'}.")
            if has_boundary_mismatch:
                rationale.append(f"Point-in-polygon conflict: Coordinates lie in district '{boundary.detected_district}', contradicting asserted district.")
            
            return VerificationDecision(
                status=VerificationStatus.INCONSISTENT,
                summary="Important address components conflict with authoritative administrative or geometric boundaries.",
                decision_rationale=rationale,
                contributing_factors=factors,
                confidence_level="HIGH"
            )

        # Rule 3: Cross-Jurisdictional Ambiguity -> AMBIGUOUS
        if is_ambiguous:
            if ambiguity_details and ambiguity_details.ambiguity_reason:
                rationale.append(ambiguity_details.ambiguity_reason)
            else:
                rationale.append("Query matches multiple distinct geographic entities across different districts/states without distinguishing context.")
            
            return VerificationDecision(
                status=VerificationStatus.AMBIGUOUS,
                summary="Multiple distinct geographic locations match the supplied information. Additional context or PIN code is required.",
                decision_rationale=rationale,
                contributing_factors=factors,
                confidence_level="HIGH"
            )

        # Rule 4: Postal Mismatch or Low Consistency Score -> NEEDS_REVIEW
        if has_pin_mismatch or consistency_score < 60:
            if has_pin_mismatch:
                rationale.append(f"PIN code '{pin.pincode}' does not match the asserted state or district records.")
            if consistency_score < 60:
                rationale.append(f"Consistency score ({consistency_score}/100) is below the automated acceptance threshold (60/100).")
            
            return VerificationDecision(
                status=VerificationStatus.NEEDS_REVIEW,
                summary="Some evidence discrepancies or incomplete data detected. Human verification recommended.",
                decision_rationale=rationale,
                contributing_factors=factors,
                confidence_level="MEDIUM"
            )

        # Rule 5: High Confidence Verified -> VERIFIED
        has_boundary_conflict = (boundary.point_inside_district is False and boundary.detected_district is not None)
        if consistency_score >= 80 and hierarchy.is_consistent and not has_boundary_conflict:
            rationale.append(f"High consistency score ({consistency_score}/100) with complete administrative alignment.")
            if boundary.point_inside_district:
                rationale.append("Spatial point-in-polygon verification confirmed within authoritative boundary polygons.")
            else:
                rationale.append("Administrative hierarchy fully consistent across state and district records.")
            if pin.pincode and pin.matched:
                rationale.append(f"PIN code '{pin.pincode}' verified with India Post postal directory.")

            return VerificationDecision(
                status=VerificationStatus.VERIFIED,
                summary="Strong geographic, administrative, and geometric consistency verified across all signals.",
                decision_rationale=rationale,
                contributing_factors=factors,
                confidence_level="HIGH"
            )

        # Rule 6: Consistent Standard Case -> CONSISTENT
        rationale.append(f"Authoritative evidence aligns with consistent hierarchy ({consistency_score}/100 score).")
        return VerificationDecision(
            status=VerificationStatus.CONSISTENT,
            summary="Geographically consistent. Most authoritative evidence aligns with minor non-critical omissions.",
            decision_rationale=rationale,
            contributing_factors=factors,
            confidence_level="HIGH" if consistency_score >= 70 else "MEDIUM"
        )


decision_engine = VerificationDecisionEngine()
