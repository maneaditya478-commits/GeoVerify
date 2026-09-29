"""Phase 2 tests for real Indian geographic datasets, LGD codes, multilingual parsing, and API endpoints."""

import json
from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.verification.hierarchy import hierarchy_validator
from app.verification.boundaries import boundary_service
from app.verification.engine import verification_engine
from app.schemas.address import Coordinates, VerificationRequest
from app.schemas.verification import VerificationStatus


def test_real_states_catalog():
    """Verify that all 36 Indian States and Union Territories are loaded with LGD and ISO codes."""
    assert len(hierarchy_validator.states) == 36
    state_codes = {s["code"] for s in hierarchy_validator.states}
    assert "MH" in state_codes  # Maharashtra
    assert "KA" in state_codes  # Karnataka
    assert "DL" in state_codes  # Delhi
    assert "TN" in state_codes  # Tamil Nadu
    assert "TG" in state_codes  # Telangana
    assert "GJ" in state_codes  # Gujarat
    assert "WB" in state_codes  # West Bengal
    assert "UP" in state_codes  # Uttar Pradesh
    assert "RJ" in state_codes  # Rajasthan
    assert "KL" in state_codes  # Kerala
    assert "LA" in state_codes  # Ladakh
    assert "JK" in state_codes  # Jammu and Kashmir
    assert "GA" in state_codes  # Goa
    assert "SK" in state_codes  # Sikkim


def test_real_districts_and_subdistricts():
    """Verify districts and subdistricts across different administrative types."""
    assert len(hierarchy_validator.districts) >= 15
    assert len(hierarchy_validator.subdistricts) >= 5

    admin_types = {sd.get("admin_type") for sd in hierarchy_validator.subdistricts}
    assert "Taluka" in admin_types
    assert "Subdivision" in admin_types or "Block" in admin_types


def test_multilingual_hierarchy_resolution():
    """Test resolution of Hindi and Marathi script entity names."""
    res_mr = hierarchy_validator.validate_hierarchy(
        state="महाराष्ट्र",
        district="पुणे",
        locality="खराडी"
    )
    assert res_mr.is_consistent is True
    assert res_mr.state == "Maharashtra"
    assert res_mr.district == "Pune"


def test_subdistrict_containment():
    """Test geometric Point-in-Polygon containment down to Sub-district level."""
    kharadi_coords = Coordinates(latitude=18.5514, longitude=73.9405)
    boundary_res = boundary_service.verify_boundaries(
        coordinates=kharadi_coords,
        asserted_state="Maharashtra",
        asserted_district="Pune",
        asserted_subdistrict="Haveli",
        asserted_locality="Kharadi"
    )
    assert boundary_res.point_inside_state is True
    assert boundary_res.point_inside_district is True
    assert boundary_res.point_inside_subdistrict is True
    assert boundary_res.detected_subdistrict == "Haveli"


@pytest.mark.asyncio
async def test_geography_api_states():
    """Test GET /api/geography/states endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/geography/states")
    assert resp.status_code == 200
    states = resp.json()
    assert len(states) == 36
    mh = next(s for s in states if s["code"] == "MH")
    assert mh["name"] == "Maharashtra"
    assert mh["lgd_code"] == 27


@pytest.mark.asyncio
async def test_geography_api_districts_filter():
    """Test GET /api/geography/districts?state_code=MH endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/geography/districts?state_code=MH")
    assert resp.status_code == 200
    districts = resp.json()
    assert len(districts) >= 5
    assert all(d["state_code"] == "MH" for d in districts)


@pytest.mark.asyncio
async def test_geography_api_search_multilingual():
    """Test GET /api/geography/search endpoint with English and Devanagari."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp_en = await ac.get("/api/geography/search?q=Bengaluru")
        resp_hi = await ac.get("/api/geography/search?q=पुणे")
    assert resp_en.status_code == 200
    assert resp_en.json()["total_matches"] > 0
    assert resp_hi.status_code == 200
    assert resp_hi.json()["total_matches"] > 0


@pytest.mark.asyncio
async def test_real_world_address_fixtures():
    """Verify all real-world test cases from tests/fixtures/real_world_addresses.json."""
    fixtures_file = Path(__file__).parent.parent.parent / "tests" / "fixtures" / "real_world_addresses.json"
    assert fixtures_file.exists()

    cases = json.loads(fixtures_file.read_text(encoding="utf-8"))
    assert len(cases) >= 10

    for tc in cases:
        req = VerificationRequest(address=tc["address"])
        res = await verification_engine.verify(req)

        expected_status = tc["expected_status"]
        if expected_status == "VERIFIED":
            assert res.status in [VerificationStatus.VERIFIED, VerificationStatus.CONSISTENT], f"Failed on fixture {tc['id']}"
            if "min_score" in tc:
                assert res.score >= tc["min_score"], f"Score too low for fixture {tc['id']}: {res.score}"
        elif expected_status == "INCONSISTENT":
            assert res.status == VerificationStatus.INCONSISTENT, f"Expected INCONSISTENT for {tc['id']}, got {res.status}"
        elif expected_status == "AMBIGUOUS":
            assert res.status in [VerificationStatus.AMBIGUOUS, VerificationStatus.NEEDS_REVIEW], f"Failed on ambiguous {tc['id']}"
        elif expected_status == "NEEDS_REVIEW":
            assert res.status == VerificationStatus.NEEDS_REVIEW, f"Failed on review fixture {tc['id']}"

        # Verify data sources attribution is included
        assert len(res.data_sources) >= 3
