"""Phase 3 tests for Ambiguity Detection and Address Completeness Scoring."""

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.entity_resolution.ambiguity import ambiguity_detector
from app.entity_resolution.resolver import address_entity_resolver
from app.services.address_parser import AddressParser
from app.schemas.address import FreeFormAddressRequest


def test_ambiguity_detection_rampur():
    """Verify that Rampur is detected as ambiguous without distinguishing state or district context."""
    res = address_entity_resolver.resolve_address("Rampur")
    assert res.ambiguity.is_ambiguous is True
    assert "matches multiple distinct locations" in res.ambiguity.ambiguity_reason
    assert len(res.ambiguity.suggested_disambiguations) >= 2
    assert any("State" in s for s in res.ambiguity.suggested_disambiguations)


def test_ambiguity_resolution_with_state_context():
    """Verify that providing state/district context resolves the ambiguity."""
    res = address_entity_resolver.resolve_address("Rampur, Uttar Pradesh")
    # With state context specified, top candidate will have a higher match score and no ambiguity conflict
    assert res.resolved_entities["state"] is not None
    assert res.resolved_entities["state"].name == "Uttar Pradesh"


def test_completeness_full_address():
    """Verify Address Completeness Score for full address vs partial inputs."""
    full_addr = AddressParser.parse("Flat 402, Ganga Carnation, Near EON Free Zone, Kharadi, Haveli, Pune, Maharashtra 411014")
    comp_full = address_entity_resolver.calculate_completeness(full_addr)
    assert comp_full.score >= 90
    assert comp_full.rating == "COMPLETE"
    assert comp_full.criteria.has_state is True
    assert comp_full.criteria.has_district is True
    assert comp_full.criteria.has_locality is True
    assert comp_full.criteria.has_pincode is True

    # Locality only
    partial_addr = AddressParser.parse("Kharadi")
    comp_partial = address_entity_resolver.calculate_completeness(partial_addr)
    assert comp_partial.score < 50
    assert "State" in comp_partial.missing_fields
    assert "District / City" in comp_partial.missing_fields


@pytest.mark.asyncio
async def test_api_ambiguity_endpoint():
    """Test POST /api/address/ambiguity endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {"address": "Rampur"}
        resp = await ac.post("/api/address/ambiguity", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_ambiguous"] is True
    assert len(data["suggested_disambiguations"]) > 0


@pytest.mark.asyncio
async def test_api_completeness_endpoint():
    """Test POST /api/address/completeness endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {"address": "Kharadi, Pune, Maharashtra 411014"}
        resp = await ac.post("/api/address/completeness", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["score"] >= 80
    assert data["rating"] in ["COMPLETE", "ADEQUATE"]
    assert "breakdown" in data


def test_completeness_missing_mandatory_fields_empty():
    """Verify empty or minimal address returns MINIMAL rating and 0 score."""
    empty_addr = AddressParser.parse("")
    comp = address_entity_resolver.calculate_completeness(empty_addr)
    assert comp.score == 0
    assert comp.rating == "MINIMAL"
    assert len(comp.missing_fields) >= 4


def test_completeness_partial_street_address():
    """Verify street address without state/pin receives PARTIAL rating."""
    addr = AddressParser.parse("Shop 12, Main Street, Kharadi")
    comp = address_entity_resolver.calculate_completeness(addr)
    assert 20 <= comp.score <= 65
    assert comp.rating in ["PARTIAL", "MINIMAL"]
    assert "State" in comp.missing_fields


def test_ambiguity_detector_direct_call():
    """Test direct check of ambiguity detector with multiple candidate matches."""
    from app.entity_resolution.models import CandidateEntity, EntityType, EntityMatchResult, EntityMatchBreakdown
    cand1 = CandidateEntity(id="d1", name="Bilaspur", entity_type=EntityType.DISTRICT, state="Chhattisgarh", similarity_score=1.0)
    cand2 = CandidateEntity(id="d2", name="Bilaspur", entity_type=EntityType.DISTRICT, state="Himachal Pradesh", similarity_score=1.0)
    b1 = EntityMatchBreakdown(name_similarity=40.0, admin_context=20.0, pin_compatibility=10.0, geographic_proximity=10.0, entity_type_weight=5.0, total_score=85.0)
    m1 = EntityMatchResult(candidate=cand1, match_score=85.0, breakdown=b1, match_confidence="HIGH")
    m2 = EntityMatchResult(candidate=cand2, match_score=85.0, breakdown=b1, match_confidence="HIGH")
    res = ambiguity_detector.detect_ambiguity([m1, m2])
    assert res.is_ambiguous is True
    assert len(res.suggested_disambiguations) >= 1

