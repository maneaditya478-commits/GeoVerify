"""API Endpoints integration tests."""

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "GeoVerify" in data["app_name"]


@pytest.mark.asyncio
async def test_parse_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/address/parse", json={"address": "Kharadi, Pune, Maharashtra 411014"})
    assert response.status_code == 200
    data = response.json()
    assert data["locality"] == "Kharadi"
    assert data["state"] == "Maharashtra"
    assert data["pincode"] == "411014"


@pytest.mark.asyncio
async def test_normalize_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/address/normalize", json={
            "address_line": "Near EON Free Zone, Kharadi",
            "city": "Poona",
            "state": "Maharastra",
            "pincode": "411 014"
        })
    assert response.status_code == 200
    data = response.json()
    assert data["district"] == "Pune"
    assert data["state"] == "Maharashtra"
    assert data["pincode"] == "411014"


@pytest.mark.asyncio
async def test_verify_endpoint_valid():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/verify", json={"address": "Kharadi, Pune, Maharashtra 411014"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["VERIFIED", "CONSISTENT"]
    assert data["score"] >= 85
    assert len(data["evidence"]) > 0
    assert len(data["explanation"]) > 0


@pytest.mark.asyncio
async def test_nearby_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/nearby?latitude=18.5514&longitude=73.9405&radius_km=5.0")
    assert response.status_code == 200
    data = response.json()
    assert data["total_found"] > 0
    assert len(data["places"]) > 0
