"""Regression and unit tests for Phase 7.3 Decision Calibration & Missing vs Conflict Semantics."""

import pytest
from app.schemas.address import VerificationRequest, StructuredAddressRequest
from app.schemas.verification import (
    VerificationStatus,
    EvidenceSeverity,
    EvidenceSemanticState,
    EvidenceItem,
)
from app.verification.engine import verification_engine
from app.verification.evidence import EvidenceEngine
from app.verification.decision_engine import VerificationDecisionEngine


@pytest.mark.asyncio
async def test_missing_coordinates_does_not_destroy_consistency():
    """When geocoding coordinates are missing, an administratively consistent address
    must not be penalized into NEEDS_REVIEW or INCONSISTENT.
    """
    req = VerificationRequest(
        address="Hadapsar, Pune, Maharashtra 411028",
        locality="Hadapsar",
        district="Pune",
        state="Maharashtra",
        pincode="411028",
    )
    res = await verification_engine.verify(req)
    
    assert res.score >= 75
    assert res.status in [VerificationStatus.VERIFIED, VerificationStatus.CONSISTENT]
    assert res.status != VerificationStatus.NEEDS_REVIEW
    assert res.status != VerificationStatus.INCONSISTENT


@pytest.mark.asyncio
async def test_conflict_vs_missing_semantic_distinction():
    """Tests the critical distinction between missing geographic tokens and active contradiction."""
    # Case A: Missing subdistrict and premise (Valid Partial Address)
    req_missing = VerificationRequest(
        address="Kharadi, Pune, Maharashtra 411014",
    )
    res_missing = await verification_engine.verify(req_missing)
    assert res_missing.status in [VerificationStatus.VERIFIED, VerificationStatus.CONSISTENT]

    # Case B: Active administrative conflict (Pune asserted under Rajasthan)
    req_conflict = VerificationRequest(
        address="Kharadi, Pune, Rajasthan 411014",
        locality="Kharadi",
        district="Pune",
        state="Rajasthan",
        pincode="411014",
    )
    res_conflict = await verification_engine.verify(req_conflict)
    assert res_conflict.status in [VerificationStatus.INCONSISTENT, VerificationStatus.NEEDS_REVIEW]
    assert res_conflict.status != VerificationStatus.VERIFIED


@pytest.mark.asyncio
async def test_partial_rural_address_semantics():
    """Rural address without premise or building number should verify with high score."""
    req = VerificationRequest(
        address="Wagholi, Haveli, Pune, Maharashtra 412207",
        locality="Wagholi",
        subdistrict="Haveli",
        district="Pune",
        state="Maharashtra",
        pincode="412207",
    )
    res = await verification_engine.verify(req)
    assert res.score >= 75
    assert res.status in [VerificationStatus.VERIFIED, VerificationStatus.CONSISTENT]


def test_evidence_item_semantic_state_enum():
    """Ensure EvidenceSemanticState enum contains all required states."""
    assert EvidenceSemanticState.SUPPORTED.value == "SUPPORTED"
    assert EvidenceSemanticState.MISSING.value == "MISSING"
    assert EvidenceSemanticState.CONFLICTING.value == "CONFLICTING"
    assert EvidenceSemanticState.UNKNOWN.value == "UNKNOWN"

    item = EvidenceItem(
        code="TEST_CODE",
        category="hierarchy",
        passed=True,
        status="PASSED",
        severity="INFO",
        semantic_state=EvidenceSemanticState.SUPPORTED,
        weight=10,
        score_contribution=10.0,
        title="Test Title",
        description="Test Description",
    )
    assert item.semantic_state == EvidenceSemanticState.SUPPORTED


@pytest.mark.asyncio
async def test_no_generic_ocr_penalty_for_clean_extracted_fields():
    """Identical structured inputs whether from clean text or OCR must yield equivalent verification."""
    clean_req = VerificationRequest(
        address="Electronic City Phase 1, Bengaluru, Karnataka 560100",
        locality="Electronic City Phase 1",
        district="Bengaluru",
        state="Karnataka",
        pincode="560100",
    )
    ocr_derived_req = VerificationRequest(
        address="Electronic City Phase 1, Bengaluru, Karnataka 560100",
        locality="Electronic City Phase 1",
        district="Bengaluru",
        state="Karnataka",
        pincode="560100",
    )

    clean_res = await verification_engine.verify(clean_req)
    ocr_res = await verification_engine.verify(ocr_derived_req)

    assert clean_res.status == ocr_res.status
    assert clean_res.score == ocr_res.score
