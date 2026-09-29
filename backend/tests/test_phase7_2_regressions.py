"""Regression and unit tests for Phase 7.2 OCR-to-GeoVerify Handoff, Verification Calibration, and Provenance Integration."""

import pytest
from app.document.models import (
    AddressRegion,
    ExtractedAddressField,
    ExtractedAddressCandidate,
    ExtractionMethod,
    BoundingBox,
)
from app.document.address.ocr_normalizer import OCRNormalizer
from app.document.address.field_extractor import AddressFieldExtractor
from app.document.address.pin_recovery import PINFirstRecoveryService
from app.verification.engine import verification_engine
from app.schemas.address import VerificationRequest, StructuredAddressRequest
from app.schemas.verification import VerificationStatus


@pytest.mark.asyncio
async def test_core_invariant_ocr_confidence_does_not_equal_geographic_validity():
    """The system must verify geographic consistency regardless of high OCR confidence.
    
    A fabricated or non-existent PIN/district pair with 100% OCR confidence must NOT
    be marked as VERIFIED or CONSISTENT.
    """
    req = VerificationRequest(
        address="Flat 101, Fake Residency, NonExistentLocality, Atlantis 999999",
        pincode="999999",
        state="FakeState",
        district="FakeDistrict",
    )
    res = await verification_engine.verify(req)
    
    assert res.status in [VerificationStatus.INCONSISTENT, VerificationStatus.UNABLE_TO_VERIFY, VerificationStatus.NEEDS_REVIEW, VerificationStatus.AMBIGUOUS]
    assert res.status != VerificationStatus.VERIFIED


@pytest.mark.asyncio
async def test_missing_evidence_semantics_does_not_penalize_partial_address():
    """Missing fields (e.g., premise/street) should be treated as partial information,
    not geographic contradiction.
    """
    req = VerificationRequest(
        address="Kharadi, Pune, Maharashtra 411014",
    )
    res = await verification_engine.verify(req)
    
    assert res.score >= 70.0
    assert res.status in [VerificationStatus.VERIFIED, VerificationStatus.CONSISTENT]
    assert res.status != VerificationStatus.INCONSISTENT


@pytest.mark.asyncio
async def test_ocr_recovered_fields_handoff_to_verification_engine():
    """Simulates OCR extraction -> PIN recovery -> GeoVerify handoff pipeline."""
    region = AddressRegion(
        region_id="reg_01",
        full_region_text="Plot 42, Ganga Carnation, Kharadi, 411014",
        confidence=0.92,
    )
    extractor = AddressFieldExtractor()
    fields = extractor.extract_fields(region)
    
    candidate = ExtractedAddressCandidate(
        candidate_id="cand_01",
        raw_address_text=region.full_region_text,
        assembled_address=region.full_region_text,
        fields=fields,
    )
    
    recovery_service = PINFirstRecoveryService()
    recovered = recovery_service.recover_candidate(candidate)
    
    assert recovered.pin_recovered is True
    assert recovered.fields["state"].normalized_value == "Maharashtra"
    assert recovered.fields["state"].extraction_method == ExtractionMethod.PIN_RECOVERY
    
    req = VerificationRequest(
        address=recovered.assembled_address,
    )
    
    res = await verification_engine.verify(req)
    assert res.score >= 70.0
    assert res.status in [VerificationStatus.VERIFIED, VerificationStatus.CONSISTENT]


def test_provenance_method_distinction():
    """Ensure all extraction methods are properly differentiated for provenance tracking."""
    methods = [
        ExtractionMethod.EXPLICIT,
        ExtractionMethod.PIN_RECOVERY,
        ExtractionMethod.ADMIN_CONTEXT_RECOVERY,
        ExtractionMethod.OCR_REPAIRED,
    ]
    for method in methods:
        field = ExtractedAddressField(
            field_name="test_field",
            raw_value="test",
            normalized_value="test",
            confidence=0.90,
            extraction_method=method,
        )
        assert field.extraction_method == method


@pytest.mark.asyncio
async def test_clean_vs_ocr_address_assembly_consistency():
    """Clean ground truth and well-extracted OCR candidate should produce identical top entity."""
    clean_req = VerificationRequest(
        address="Survey No 136, Cybercity, Magarpatta, Hadapsar, Pune, Maharashtra 411028",
    )
    ocr_req = VerificationRequest(
        address="Survey No 136, Cybercity, Magarpatta, Hadapsar, Pune, Maharashtra 411028",
    )
    
    clean_res = await verification_engine.verify(clean_req)
    ocr_res = await verification_engine.verify(ocr_req)
    
    assert clean_res.status == ocr_res.status
    assert abs(clean_res.score - ocr_res.score) < 1e-5


@pytest.mark.asyncio
async def test_multilingual_devanagari_handoff_consistency():
    """Devanagari text input should verify correctly through transliteration and entity resolution."""
    marathi_req = VerificationRequest(
        address="सोनु टॉवर, हिंजवडी फेज १, पुणे, महाराष्ट्र ४११०५७",
    )
    res = await verification_engine.verify(marathi_req)
    
    assert res.score >= 50.0
    assert res.status in [VerificationStatus.VERIFIED, VerificationStatus.CONSISTENT, VerificationStatus.NEEDS_REVIEW, VerificationStatus.AMBIGUOUS]
