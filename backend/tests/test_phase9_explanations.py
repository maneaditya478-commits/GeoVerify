"""Unit and integration tests for Phase 9 Explainable Verification API."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.schemas.address import VerificationRequest
from app.schemas.verification import VerificationStatus


@pytest.mark.asyncio
async def test_explain_endpoint_complete_narrative():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        req_body = {
            "address": "Flat 302, Near Shaniwar Wada, Kothrud, Poona, Maharashtra 411038",
            "reference_date": "1985-05-20",
            "historical_context": True,
            "research_mode": True
        }
        res = await ac.post("/api/verify/explain", json=req_body)
        assert res.status_code == 200
        data = res.json()

        assert "verification_id" in data
        assert "confidence_profile" in data
        assert data["confidence_profile"]["is_calibrated"] is True
        assert len(data["temporal_evidence"]) >= 1
        assert any(t["canonical_current_name"] == "Pune" for t in data["temporal_evidence"])
        assert len(data["landmark_evidence"]) >= 1
        assert any("Shaniwar Wada" in l["landmark_name"] for l in data["landmark_evidence"])
        assert "multilingual_breakdown" in data
        assert len(data["explanation_narrative"]) >= 3


@pytest.mark.asyncio
async def test_standard_verify_endpoint_includes_phase9_payload():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        req_body = {
            "address": "Opposite IIT Bombay, Powai, Bombay 400076",
            "reference_date": "1990-01-01"
        }
        res = await ac.post("/api/verify", json=req_body)
        assert res.status_code == 200
        data = res.json()

        assert data["confidence_profile"] is not None
        assert len(data["temporal_evidence"]) >= 1
        assert len(data["landmark_evidence"]) >= 1
