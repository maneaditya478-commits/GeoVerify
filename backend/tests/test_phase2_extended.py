"""Extended Phase 2 tests for PIN validation breakdown, multilingual names, and database entities."""

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.services.pin_validator import PinValidator, haversine_distance
from app.services.normalizer import AddressNormalizer
from app.services.address_parser import AddressParser
from app.schemas.address import Coordinates, VerificationRequest
from app.verification.boundaries import boundary_service
from app.verification.hierarchy import hierarchy_validator
from app.verification.scoring import ScoringEngine
from app.schemas.verification import EvidenceItem, BoundaryVerificationResult, PinVerificationResult
from app.schemas.hierarchy import AdministrativeHierarchyResult


def test_pin_validator_separated_breakdown():
    """Verify that PIN validation separates format, circle, district, and centroid distance."""
    validator = PinValidator()
    coords = Coordinates(latitude=18.5514, longitude=73.9405)
    res = validator.validate("411014", state="Maharashtra", district="Pune", coordinates=coords)

    assert res.is_valid_format is True
    assert res.matched is True
    assert res.matched_state == "Maharashtra"
    assert res.matched_district == "Pune"
    assert res.distance_to_coordinates_km is not None
    assert res.distance_to_coordinates_km < 10.0
    assert "India Post" in res.source


def test_pin_validator_circle_mismatch_isolated():
    """Test circle mismatch when 560066 (Karnataka) is paired with Maharashtra."""
    validator = PinValidator()
    res = validator.validate("560066", state="Maharashtra", district="Pune")
    assert res.is_valid_format is True
    assert res.matched is False
    assert "Karnataka" in res.evidence


def test_haversine_distance_calculation():
    """Test Haversine distance accuracy between Pune and Mumbai."""
    pune = Coordinates(latitude=18.5204, longitude=73.8567)
    mumbai = Coordinates(latitude=19.0760, longitude=72.8777)
    dist = haversine_distance(pune, mumbai)
    # Approx 120-130 km
    assert 115.0 <= dist <= 135.0


def test_multilingual_state_normalization():
    """Test normalization of Hindi and Marathi state names."""
    state, code, trans = AddressNormalizer.normalize_state("महाराष्ट्र")
    assert state == "Maharashtra"
    assert code == "MH"

    state_ka, code_ka, trans_ka = AddressNormalizer.normalize_state("कर्नाटक")
    assert state_ka == "Karnataka"
    assert code_ka == "KA"


def test_multilingual_district_aliases():
    """Test normalization of district aliases."""
    dist_bom, _ = AddressNormalizer.normalize_district("Bombay")
    assert dist_bom == "Mumbai Suburban"

    dist_cal, _ = AddressNormalizer.normalize_district("Calcutta")
    assert dist_cal == "Kolkata"

    dist_mad, _ = AddressNormalizer.normalize_district("Madras")
    assert dist_mad == "Chennai"


def test_address_parser_multiple_landmarks():
    """Test parsing multiple landmarks and premise numbers."""
    raw = "Shop 12, Opposite Inorbit Mall, Near Phoenix Marketcity, Viman Nagar, Pune, MH 411014"
    parsed = AddressParser.parse(raw)
    assert parsed.locality == "Viman Nagar"
    assert parsed.district == "Pune"
    assert parsed.state == "Maharashtra"
    assert parsed.pincode == "411014"
    assert len(parsed.landmarks) >= 1
    assert parsed.parse_confidence == 1.0


def test_subdistrict_admin_type_support():
    """Test recognition of different Indian administrative types (Taluka vs Subdivision)."""
    # Haveli (Taluka) in Maharashtra
    res_taluka = hierarchy_validator.validate_hierarchy(
        state="Maharashtra",
        district="Pune",
        subdistrict="Haveli",
        locality="Kharadi"
    )
    assert res_taluka.is_consistent is True
    assert any("Taluka" in n.evidence for n in res_taluka.hierarchy_chain if n.evidence)

    # Chanakyapuri (Subdivision) in Delhi
    res_subdiv = hierarchy_validator.validate_hierarchy(
        state="Delhi",
        district="New Delhi",
        subdistrict="Chanakyapuri",
        locality="Connaught Place"
    )
    assert res_subdiv.is_consistent is True


def test_boundary_outside_subdistrict():
    """Test point falling outside asserted subdistrict boundary."""
    # Coordinates in Mulshi (Hinjewadi)
    hinjewadi_coords = Coordinates(latitude=18.5913, longitude=73.7389)
    res = boundary_service.verify_boundaries(
        coordinates=hinjewadi_coords,
        asserted_state="Maharashtra",
        asserted_district="Pune",
        asserted_subdistrict="Haveli"  # Incorrect subdistrict, it's in Mulshi
    )
    assert res.point_inside_subdistrict is False
    assert res.detected_subdistrict == "Mulshi"


@pytest.mark.asyncio
async def test_geography_api_subdistricts_filter():
    """Test GET /api/geography/subdistricts?district_id=dist_pune."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/geography/subdistricts?district_id=dist_pune")
    assert resp.status_code == 200
    subdistricts = resp.json()
    assert len(subdistricts) >= 3
    assert any(sd["name"] == "Haveli" for sd in subdistricts)


@pytest.mark.asyncio
async def test_geography_search_no_match():
    """Test search with non-existent query."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/geography/search?q=NonExistentLocality12345")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_matches"] == 0


def test_scoring_boundary_weights():
    """Verify that scoring engine properly balances boundary and hierarchy signals."""
    evidence = [
        EvidenceItem(code="STATE_OK", category="hierarchy", passed=True, status="PASSED", weight=10, score_contribution=10, title="State", description="State match"),
        EvidenceItem(code="DIST_OK", category="hierarchy", passed=True, status="PASSED", weight=15, score_contribution=15, title="District", description="District match"),
        EvidenceItem(code="BOUND_STATE", category="boundary", passed=True, status="PASSED", weight=10, score_contribution=10, title="Boundary State", description="In state"),
        EvidenceItem(code="BOUND_DIST", category="boundary", passed=True, status="PASSED", weight=15, score_contribution=15, title="Boundary District", description="In district"),
    ]
    hierarchy = AdministrativeHierarchyResult(state="Maharashtra", district="Pune", is_consistent=True)
    boundary = BoundaryVerificationResult(point_inside_state=True, point_inside_district=True)
    pin = PinVerificationResult(pincode="411014", is_valid_format=True, matched=True)

    score, breakdown, status, _ = ScoringEngine.calculate_score(evidence, hierarchy, boundary, pin)
    assert breakdown.hierarchy_score == 25.0
    assert breakdown.boundary_score == 25.0


@pytest.mark.asyncio
async def test_verification_response_data_sources():
    """Verify that full verification response includes authoritative data source attributions."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {"address": "EON IT Park, Kharadi, Pune, Maharashtra 411014"}
        resp = await ac.post("/api/verify", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "data_sources" in data
    assert len(data["data_sources"]) >= 3
    source_names = [s["name"] for s in data["data_sources"]]
    assert any("LGD" in s for s in source_names)
    assert any("India Post" in s for s in source_names)


@pytest.mark.asyncio
async def test_geography_api_pincode_lookup():
    """Test GET /api/geography/pincode/{pincode} endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/geography/pincode/560066")
    assert resp.status_code == 200
    pin_data = resp.json()
    assert pin_data["pincode"] == "560066"
    assert pin_data["state"] == "Karnataka"
    assert pin_data["district"] == "Bengaluru Urban"


def test_dataset_provenance_integrity():
    """Verify that processed datasets have proper provenance and no empty structures."""
    from pathlib import Path
    import json
    data_dir = Path(__file__).parent.parent.parent / "data" / "processed"
    assert (data_dir / "states.json").exists()
    assert (data_dir / "districts.json").exists()
    assert (data_dir / "subdistricts.json").exists()
    assert (data_dir / "pincodes.json").exists()

    with open(data_dir / "states.json", "r", encoding="utf-8") as f:
        states = json.load(f)
    assert len(states) == 36
    assert all("lgd_code" in s for s in states)
    assert all("source" in s for s in states)


@pytest.mark.asyncio
async def test_subdistrict_in_verification_pipeline():
    """Verify full verification workflow when address explicitly includes subdistrict."""
    from app.verification.engine import verification_engine
    req = VerificationRequest(
        address="World Trade Center, Kharadi, Haveli, Pune, Maharashtra 411014",
        include_geometry=True
    )
    res = await verification_engine.verify(req)
    assert res.status == "VERIFIED"
    assert res.score >= 80.0
    assert res.administrative_hierarchy.subdistrict == "Haveli"
    assert res.boundary_verification.point_inside_subdistrict is True

