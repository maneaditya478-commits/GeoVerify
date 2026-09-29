"""Tests for Verification Scoring & Status resolution."""

import pytest
from app.schemas.verification import (
    EvidenceItem,
    BoundaryVerificationResult,
    PinVerificationResult,
    VerificationStatus
)
from app.schemas.hierarchy import AdministrativeHierarchyResult
from app.verification.scoring import ScoringEngine


def test_scoring_engine_verified():
    evidence = [
        EvidenceItem(code="STATE_VERIFIED", category="hierarchy", passed=True, status="PASSED", weight=10, score_contribution=10, title="State", description="State match"),
        EvidenceItem(code="DISTRICT_VERIFIED", category="hierarchy", passed=True, status="PASSED", weight=15, score_contribution=15, title="District", description="District match"),
        EvidenceItem(code="BOUNDARY_STATE", category="boundary", passed=True, status="PASSED", weight=10, score_contribution=10, title="Boundary State", description="In state"),
        EvidenceItem(code="BOUNDARY_DISTRICT", category="boundary", passed=True, status="PASSED", weight=15, score_contribution=15, title="Boundary District", description="In district"),
        EvidenceItem(code="LOCALITY_MATCH", category="locality", passed=True, status="PASSED", weight=20, score_contribution=20, title="Locality", description="Locality verified"),
        EvidenceItem(code="PIN_MATCH", category="pincode", passed=True, status="PASSED", weight=15, score_contribution=15, title="PIN", description="PIN verified"),
        EvidenceItem(code="GEO_RESOLVED", category="geocoding", passed=True, status="PASSED", weight=10, score_contribution=9.5, title="Geocoding", description="Geocoded"),
        EvidenceItem(code="NEARBY_CONFIRMED", category="nearby", passed=True, status="PASSED", weight=5, score_contribution=5, title="Nearby", description="Nearby POIs found"),
    ]
    hierarchy = AdministrativeHierarchyResult(state="Maharashtra", district="Pune", is_consistent=True)
    boundary = BoundaryVerificationResult(point_inside_state=True, point_inside_district=True)
    pin = PinVerificationResult(pincode="411014", is_valid_format=True, matched=True)

    score, breakdown, status, summary = ScoringEngine.calculate_score(evidence, hierarchy, boundary, pin)
    assert score >= 90
    assert status == VerificationStatus.VERIFIED


def test_scoring_engine_inconsistent():
    evidence = [
        EvidenceItem(code="DISTRICT_MISMATCH", category="hierarchy", passed=False, status="FAILED", weight=15, score_contribution=0, title="District", description="District mismatch"),
    ]
    hierarchy = AdministrativeHierarchyResult(state="Maharashtra", district="Kolhapur", is_consistent=False, mismatch_details=["District mismatch"])
    boundary = BoundaryVerificationResult(point_inside_state=True, point_inside_district=False, detected_district="Pune")
    pin = PinVerificationResult(pincode="411014", is_valid_format=True, matched=False)

    score, breakdown, status, summary = ScoringEngine.calculate_score(evidence, hierarchy, boundary, pin)
    assert status == VerificationStatus.INCONSISTENT
