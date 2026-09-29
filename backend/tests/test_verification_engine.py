"""Integration tests for the full verification engine."""

import pytest
from app.schemas.address import VerificationRequest, StructuredAddressRequest
from app.schemas.verification import VerificationStatus
from app.verification.engine import verification_engine


@pytest.mark.asyncio
async def test_verify_valid_kharadi_address():
    req = VerificationRequest(address="Kharadi, Pune, Maharashtra 411014")
    res = await verification_engine.verify(req)
    assert res.status in [VerificationStatus.VERIFIED, VerificationStatus.CONSISTENT]
    assert res.score >= 85
    assert res.geocoding is not None
    assert res.boundary_verification.point_inside_district is True
    assert res.pin_verification.matched is True
    assert len(res.nearby_places) > 0


@pytest.mark.asyncio
async def test_verify_district_mismatch():
    req = VerificationRequest(address="Kharadi, Kolhapur, Maharashtra")
    res = await verification_engine.verify(req)
    assert res.status == VerificationStatus.INCONSISTENT
    assert len(res.warnings) > 0


@pytest.mark.asyncio
async def test_verify_typo_address():
    req = VerificationRequest(address="Kharadi, Puna, Maharastra 411014")
    res = await verification_engine.verify(req)
    assert res.status in [VerificationStatus.VERIFIED, VerificationStatus.CONSISTENT]
    assert res.normalized_address.state == "Maharashtra"
    assert res.normalized_address.district == "Pune"


@pytest.mark.asyncio
async def test_verify_ambiguous_address():
    req = VerificationRequest(address="Rampur")
    res = await verification_engine.verify(req)
    assert res.status in [VerificationStatus.AMBIGUOUS, VerificationStatus.NEEDS_REVIEW]
