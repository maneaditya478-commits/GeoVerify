"""Phase 3 tests for Address Entity Resolution, Candidate Generation, and Match Scoring."""

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.entity_resolution.candidates import candidate_generator
from app.entity_resolution.matcher import entity_matcher
from app.entity_resolution.resolver import address_entity_resolver
from app.entity_resolution.models import EntityType
from app.schemas.address import Coordinates, FreeFormAddressRequest


def test_candidate_generator_exact_and_alias():
    """Verify candidate generation for exact match and aliases."""
    candidates = candidate_generator.generate_candidates("Pune", expected_type=EntityType.DISTRICT)
    assert len(candidates) >= 1
    assert candidates[0].name == "Pune"
    assert candidates[0].similarity_score == 1.0

    # Poona alias
    alias_candidates = candidate_generator.generate_candidates("Poona", expected_type=EntityType.DISTRICT)
    assert len(alias_candidates) >= 1
    assert alias_candidates[0].name == "Pune"
    assert alias_candidates[0].similarity_score >= 0.90


def test_candidate_generator_fuzzy():
    """Verify fuzzy matching for typos (e.g. 'Kharadii' or 'Bengalru')."""
    fuzzy_locs = candidate_generator.generate_candidates("Kharadii", expected_type=EntityType.LOCALITY)
    assert len(fuzzy_locs) >= 1
    assert fuzzy_locs[0].name == "Kharadi"
    assert fuzzy_locs[0].similarity_score >= 0.85

    fuzzy_dists = candidate_generator.generate_candidates("Bengalru", expected_type=EntityType.DISTRICT)
    assert len(fuzzy_dists) >= 1
    assert fuzzy_dists[0].name == "Bengaluru Urban"


def test_entity_matcher_score_weights():
    """Verify transparent 5-part Entity Match Score breakdown."""
    candidates = candidate_generator.generate_candidates("Kharadi", expected_type=EntityType.LOCALITY)
    assert len(candidates) >= 1
    top_cand = candidates[0]

    coords = Coordinates(latitude=18.5514, longitude=73.9405)
    match_res = entity_matcher.match_candidate(
        candidate=top_cand,
        query_text="Kharadi",
        context_state="Maharashtra",
        context_district="Pune",
        context_subdistrict="Haveli",
        context_pin="411014",
        context_coordinates=coords,
        expected_type=EntityType.LOCALITY
    )

    assert match_res.match_score >= 90.0
    assert match_res.breakdown.name_similarity == 40.0
    assert match_res.breakdown.admin_context == 25.0
    assert match_res.breakdown.pin_compatibility == 15.0
    assert match_res.breakdown.geographic_proximity == 15.0
    assert match_res.breakdown.entity_type_weight == 5.0
    assert match_res.match_confidence == "HIGH"


def test_entity_resolver_end_to_end():
    """Verify full entity resolution pipeline on a complete address."""
    addr = "World Trade Center, Kharadi, Haveli, Pune, Maharashtra 411014"
    res = address_entity_resolver.resolve_address(addr)

    assert res.resolved_entities["state"] is not None
    assert res.resolved_entities["state"].name == "Maharashtra"
    assert res.resolved_entities["district"] is not None
    assert res.resolved_entities["district"].name == "Pune"
    assert res.resolved_entities["subdistrict"] is not None
    assert res.resolved_entities["subdistrict"].name == "Haveli"
    assert res.resolved_entities["locality"] is not None
    assert res.resolved_entities["locality"].name == "Kharadi"
    assert res.entity_match_score >= 80


@pytest.mark.asyncio
async def test_api_address_resolve_endpoint():
    """Test POST /api/address/resolve endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {"address": "EON IT Park, Kharadi, Pune, Maharashtra 411014"}
        resp = await ac.post("/api/address/resolve", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "resolved_entities" in data
    assert "candidate_matches" in data
    assert "completeness" in data
    assert data["completeness"]["score"] >= 80


@pytest.mark.asyncio
async def test_api_address_candidates_endpoint():
    """Test GET /api/address/candidates?q=Kharadi endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/address/candidates?q=Kharadi&state=Maharashtra")
    assert resp.status_code == 200
    data = resp.json()
    assert data["query"] == "Kharadi"
    assert data["total_candidates"] >= 1
    assert data["candidates"][0]["candidate"]["name"] == "Kharadi"


def test_candidate_generator_state_filter():
    """Verify candidate generator prioritizes matching state when context is provided."""
    mh_candidates = candidate_generator.generate_candidates("Haveli", context_state="Maharashtra")
    assert len(mh_candidates) >= 1
    assert mh_candidates[0].state == "Maharashtra"


def test_entity_matcher_score_breakdown_mismatches():
    """Verify entity matcher applies penalties for state/district mismatches."""
    candidates = candidate_generator.generate_candidates("Kharadi", expected_type=EntityType.LOCALITY)
    assert len(candidates) >= 1
    top_cand = candidates[0]

    match_res = entity_matcher.match_candidate(
        candidate=top_cand,
        query_text="Kharadi",
        context_state="Karnataka",  # Mismatched state
        context_district="Mysuru",  # Mismatched district
        context_pin="560066",       # Mismatched PIN
        expected_type=EntityType.LOCALITY
    )
    assert match_res.breakdown.admin_context == 0.0
    assert match_res.breakdown.pin_compatibility == 0.0
    assert match_res.match_confidence == "LOW"
    assert match_res.match_score <= 55.0

