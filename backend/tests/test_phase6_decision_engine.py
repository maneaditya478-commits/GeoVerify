"""Unit and Integration Tests for Phase 6 Verification Decision Engine."""

import pytest
from app.verification.decision_engine import VerificationDecisionEngine, VerificationDecision, decision_engine
from app.schemas.verification import (
    VerificationStatus,
    BoundaryVerificationResult,
    PinVerificationResult
)
from app.schemas.hierarchy import AdministrativeHierarchyResult
from app.entity_resolution.models import AmbiguityDetails


def test_decision_engine_unable_to_verify():
    """Verify UNABLE_TO_VERIFY status when no geographic anchors are provided."""
    hierarchy = AdministrativeHierarchyResult(is_consistent=False)
    boundary = BoundaryVerificationResult()
    pin = PinVerificationResult()

    decision = decision_engine.evaluate(
        consistency_score=15,
        hierarchy=hierarchy,
        boundary=boundary,
        pin=pin
    )

    assert decision.status == VerificationStatus.UNABLE_TO_VERIFY
    assert "Insufficient" in decision.summary
    assert decision.confidence_level == "LOW"


def test_decision_engine_inconsistent_hierarchy():
    """Verify INCONSISTENT status when hierarchy relationship is invalid."""
    hierarchy = AdministrativeHierarchyResult(
        is_consistent=False,
        state="Maharashtra",
        district="Bengaluru Urban",  # Inconsistent with Maharashtra
        mismatch_details=["District 'Bengaluru Urban' does not belong to State 'Maharashtra'"]
    )
    boundary = BoundaryVerificationResult(point_inside_district=False, detected_district="Pune")
    pin = PinVerificationResult()

    decision = decision_engine.evaluate(
        consistency_score=35,
        hierarchy=hierarchy,
        boundary=boundary,
        pin=pin
    )

    assert decision.status == VerificationStatus.INCONSISTENT
    assert len(decision.decision_rationale) >= 1
    assert "Administrative hierarchy conflict" in decision.decision_rationale[0]


def test_decision_engine_ambiguous():
    """Verify AMBIGUOUS status when cross-jurisdictional ambiguity is detected."""
    hierarchy = AdministrativeHierarchyResult(is_consistent=True, locality="Rampur")
    boundary = BoundaryVerificationResult(point_inside_district=True)
    pin = PinVerificationResult()
    amb_details = AmbiguityDetails(
        is_ambiguous=True,
        ambiguity_reason="Locality matches both Rampur (UP) and Rampur (Bihar)."
    )

    decision = decision_engine.evaluate(
        consistency_score=75,
        hierarchy=hierarchy,
        boundary=boundary,
        pin=pin,
        is_ambiguous=True,
        ambiguity_details=amb_details
    )

    assert decision.status == VerificationStatus.AMBIGUOUS
    assert "Multiple distinct geographic locations" in decision.summary


def test_decision_engine_needs_review():
    """Verify NEEDS_REVIEW status on postal mismatch or moderate score."""
    hierarchy = AdministrativeHierarchyResult(is_consistent=True, state="Maharashtra", district="Pune")
    boundary = BoundaryVerificationResult(point_inside_district=True)
    pin = PinVerificationResult(pincode="110001", is_valid_format=True, matched=False)

    decision = decision_engine.evaluate(
        consistency_score=68,
        hierarchy=hierarchy,
        boundary=boundary,
        pin=pin
    )

    assert decision.status == VerificationStatus.NEEDS_REVIEW
    assert any("PIN code" in r for r in decision.decision_rationale)


def test_decision_engine_verified():
    """Verify VERIFIED status when score >= 85 and all checks pass."""
    hierarchy = AdministrativeHierarchyResult(is_consistent=True, state="Maharashtra", district="Pune", locality="Kharadi")
    boundary = BoundaryVerificationResult(point_inside_state=True, point_inside_district=True)
    pin = PinVerificationResult(pincode="411014", is_valid_format=True, matched=True)

    decision = decision_engine.evaluate(
        consistency_score=94,
        hierarchy=hierarchy,
        boundary=boundary,
        pin=pin,
        is_ambiguous=False
    )

    assert decision.status == VerificationStatus.VERIFIED
    assert decision.confidence_level == "HIGH"
    assert "Strong geographic" in decision.summary


def test_decision_engine_consistent():
    """Verify CONSISTENT status on standard valid addresses."""
    hierarchy = AdministrativeHierarchyResult(is_consistent=True, state="Karnataka", district="Bengaluru Urban")
    boundary = BoundaryVerificationResult(point_inside_state=True, point_inside_district=False)
    pin = PinVerificationResult(pincode="560034", is_valid_format=True, matched=True)

    decision = decision_engine.evaluate(
        consistency_score=78,
        hierarchy=hierarchy,
        boundary=boundary,
        pin=pin,
        is_ambiguous=False
    )

    assert decision.status == VerificationStatus.CONSISTENT
    assert "Geographically consistent" in decision.summary


def test_decision_engine_point_outside_district():
    """Verify INCONSISTENT status when point lies strictly outside asserted district."""
    hierarchy = AdministrativeHierarchyResult(is_consistent=True, state="Maharashtra", district="Pune")
    boundary = BoundaryVerificationResult(point_inside_district=False, detected_district="Thane")
    pin = PinVerificationResult(pincode="411014", is_valid_format=True, matched=True)

    decision = decision_engine.evaluate(
        consistency_score=60,
        hierarchy=hierarchy,
        boundary=boundary,
        pin=pin
    )

    assert decision.status == VerificationStatus.INCONSISTENT
    assert any("Point-in-polygon conflict" in r for r in decision.decision_rationale)


def test_decision_engine_factors_and_confidence():
    """Verify contributing factors dictionary contains expected flags and scores."""
    hierarchy = AdministrativeHierarchyResult(is_consistent=True, state="Maharashtra", district="Pune")
    boundary = BoundaryVerificationResult(point_inside_district=True)
    pin = PinVerificationResult(pincode="411014", is_valid_format=True, matched=True)

    decision = decision_engine.evaluate(
        consistency_score=92,
        hierarchy=hierarchy,
        boundary=boundary,
        pin=pin
    )

    assert decision.contributing_factors["consistency_score"] == 92
    assert decision.contributing_factors["hierarchy_consistent"] is True
    assert decision.contributing_factors["boundary_inside_district"] is True
    assert decision.contributing_factors["pin_matched"] is True
    assert decision.confidence_level == "HIGH"


def test_decision_engine_low_score_needs_review():
    """Verify score < 70 triggers NEEDS_REVIEW with score rationale."""
    hierarchy = AdministrativeHierarchyResult(is_consistent=True, state="Maharashtra")
    boundary = BoundaryVerificationResult(point_inside_district=False)
    pin = PinVerificationResult()

    decision = decision_engine.evaluate(
        consistency_score=55,
        hierarchy=hierarchy,
        boundary=boundary,
        pin=pin
    )

    assert decision.status == VerificationStatus.NEEDS_REVIEW
    assert any("below the automated acceptance threshold" in r for r in decision.decision_rationale)


def test_decision_engine_ambiguity_override():
    """Verify ambiguity reason is preserved in decision rationale."""
    hierarchy = AdministrativeHierarchyResult(is_consistent=True, locality="Bilaspur")
    boundary = BoundaryVerificationResult(point_inside_district=True)
    pin = PinVerificationResult()
    amb = AmbiguityDetails(
        is_ambiguous=True,
        ambiguity_reason="Matches Bilaspur in Chhattisgarh vs Bilaspur in Himachal Pradesh."
    )

    decision = decision_engine.evaluate(
        consistency_score=80,
        hierarchy=hierarchy,
        boundary=boundary,
        pin=pin,
        is_ambiguous=True,
        ambiguity_details=amb
    )

    assert decision.status == VerificationStatus.AMBIGUOUS
    assert "Chhattisgarh" in decision.decision_rationale[0]

