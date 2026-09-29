"""Scoring engine and status evaluator for GeoVerify India."""

from typing import List, Tuple
from app.config import settings
from app.schemas.verification import (
    VerificationStatus,
    ScoreBreakdown,
    EvidenceItem,
    BoundaryVerificationResult,
    PinVerificationResult
)
from app.schemas.hierarchy import AdministrativeHierarchyResult


class ScoringEngine:
    """Computes transparent Geographic Consistency Score and derives status."""

    @classmethod
    def calculate_score(
        cls,
        evidence_items: List[EvidenceItem],
        hierarchy: AdministrativeHierarchyResult,
        boundary: BoundaryVerificationResult,
        pin: PinVerificationResult,
        is_ambiguous: bool = False
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

        # Check for conflicts
        has_hierarchy_mismatch = (not hierarchy.is_consistent or len(hierarchy.mismatch_details) > 0) and bool(hierarchy.state or hierarchy.district or hierarchy.locality)
        has_boundary_mismatch = (boundary.point_inside_district is False and boundary.detected_district is not None)
        has_pin_mismatch = pin.pincode is not None and pin.is_valid_format and not pin.matched

        if not hierarchy.state and not hierarchy.district and not hierarchy.locality and not pin.pincode:
            status = VerificationStatus.UNABLE_TO_VERIFY
            summary = "Insufficient geographic details to verify the address."
        elif has_hierarchy_mismatch or has_boundary_mismatch:
            status = VerificationStatus.INCONSISTENT
            summary = "Important address components conflict with authoritative administrative or geometric boundaries."
        elif is_ambiguous:
            status = VerificationStatus.AMBIGUOUS
            summary = "Multiple distinct geographic locations match the supplied information. Additional context or PIN code is required."
        elif has_pin_mismatch or total_score < 70:
            status = VerificationStatus.NEEDS_REVIEW
            summary = "Some evidence discrepancies or incomplete data detected. Human verification recommended."
        elif total_score >= 85 and hierarchy.is_consistent and boundary.point_inside_district:
            status = VerificationStatus.VERIFIED
            summary = "Strong geographic, administrative, and geometric consistency verified across all signals."
        else:
            status = VerificationStatus.CONSISTENT
            summary = "Geographically consistent. Most authoritative evidence aligns with minor non-critical omissions."

        return total_score, score_breakdown, status, summary
