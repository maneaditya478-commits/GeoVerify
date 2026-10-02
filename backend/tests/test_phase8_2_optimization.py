"""Unit and integration tests for Phase 8.2 Production Optimization & Hardening."""

import pytest
import io
import time
from PIL import Image
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.config import settings
from app.core.cache import (
    BoundedLRUTTLCache,
    CryptographicCacheKeyGenerator,
    verification_cache,
    ocr_cache,
    geo_lookup_cache,
)
from app.core.errors import (
    APIErrorResponse,
    DatabaseTimeoutException,
    OCRTimeoutException,
    ResourceExhaustedException,
)
from app.schemas.address import VerificationRequest, StructuredAddressRequest
from app.document.pipeline import DocumentProcessingPipeline


@pytest.mark.asyncio
async def test_health_endpoints():
    """Verifies all Phase 8.2 monitoring and health probe endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. /health
        res = await client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["config_version"] == settings.GEOVERIFY_CONFIG_VERSION

        # 2. /health/live
        res_live = await client.get("/health/live")
        assert res_live.status_code == 200
        assert res_live.json()["status"] == "alive"

        # 3. /health/ready
        res_ready = await client.get("/health/ready")
        assert res_ready.status_code == 200
        data_ready = res_ready.json()
        assert data_ready["status"] == "ready"
        assert data_ready["checks"]["geographic_catalog"] is True
        assert data_ready["checks"]["dense_vector_index"] is True

        # 4. /health/telemetry
        res_telem = await client.get("/health/telemetry")
        assert res_telem.status_code == 200
        data_telem = res_telem.json()
        assert "cache_stats" in data_telem
        assert "verification_cache" in data_telem["cache_stats"]


def test_cryptographic_cache_key_generation():
    """Verifies SHA-256 cache key determinism and homonym collision resistance."""
    k1 = CryptographicCacheKeyGenerator.generate_key(
        query="Rampur", state="Uttar Pradesh", district="Rampur", pincode="244901"
    )
    k2 = CryptographicCacheKeyGenerator.generate_key(
        query="Rampur", state="Bihar", district="Gaya", pincode="823001"
    )
    k3 = CryptographicCacheKeyGenerator.generate_key(
        query="Rampur", state="Uttar Pradesh", district="Rampur", pincode="244901"
    )

    assert isinstance(k1, str) and len(k1) == 64  # SHA-256 hex string
    assert k1 != k2  # Different states & pincodes produce distinct keys
    assert k1 == k3  # Deterministic replay matches exactly


def test_bounded_lru_ttl_cache_eviction():
    """Verifies LRU eviction and TTL expiration in BoundedLRUTTLCache."""
    cache = BoundedLRUTTLCache(maxsize=3, ttl_seconds=1)

    # Insert 3 items
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    assert cache.stats["size"] == 3

    # Insert 4th item -> oldest 'a' should be evicted
    cache.set("d", 4)
    assert cache.stats["size"] == 3
    assert cache.stats["evictions"] == 1
    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert cache.get("c") == 3
    assert cache.get("d") == 4

    # Test TTL expiration
    time.sleep(1.1)
    assert cache.get("b") is None
    assert cache.stats["size"] == 2  # Del on get expiration


@pytest.mark.asyncio
async def test_batch_verification_endpoint():
    """Verifies POST /api/verify/batch with bounded size, ordering, and error isolation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        batch_payload = [
            {"address": "Indiranagar, Bangalore, Karnataka 560038"},
            {"address": "Kothrud, Pune, Maharashtra 411038"},
            {"address": "Connaught Place, New Delhi, Delhi 110001"},
        ]
        res = await client.post("/api/verify/batch", json=batch_payload)
        assert res.status_code == 200
        data = res.json()
        assert data["total_requested"] == 3
        assert data["successful_count"] == 3
        assert data["failed_count"] == 0
        assert len(data["results"]) == 3
        assert data["results"][0]["index"] == 0
        assert data["results"][1]["index"] == 1
        assert data["results"][2]["index"] == 2
        assert data["results"][0]["success"] is True


@pytest.mark.asyncio
async def test_batch_verification_max_bound_rejection():
    """Verifies that exceeding BATCH_MAX_SIZE is rejected cleanly."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Generate payload larger than BATCH_MAX_SIZE (50)
        large_batch = [{"address": f"Address {i}, Pune 411001"} for i in range(55)]
        res = await client.post("/api/verify/batch", json=large_batch)
        assert res.status_code == 400


@pytest.mark.asyncio
async def test_ocr_caching_and_cleanup():
    """Verifies OCR caching on identical image upload and safe cleanup."""
    img = Image.new("RGB", (600, 400), color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    raw_bytes = buf.getvalue()

    pipeline = DocumentProcessingPipeline(ocr_engine_name="mock")

    # Pass 1: Cold OCR
    res1 = await pipeline.process_document(
        file_bytes=raw_bytes,
        filename="test_cache.png",
        mime_type="image/png",
        verify_geography=False,
        engine_override="mock",
    )
    assert res1.ocr.status == "SUCCESS"

    # Pass 2: Warm OCR (Cached)
    res2 = await pipeline.process_document(
        file_bytes=raw_bytes,
        filename="test_cache.png",
        mime_type="image/png",
        verify_geography=False,
        engine_override="mock",
    )
    assert res2.ocr.status == "SUCCESS"
    assert res2.stage_timings_ms["ocr_execution_ms"] == 0.0  # From cache


def test_structured_error_responses():
    """Verifies standardized API error schemas and exceptions."""
    exc_db = DatabaseTimeoutException("Connection pool query timeout")
    assert exc_db.status_code == 504
    assert exc_db.code == "DATABASE_TIMEOUT"

    exc_ocr = OCRTimeoutException("Tesseract engine processing timeout")
    assert exc_ocr.status_code == 504
    assert exc_ocr.code == "OCR_TIMEOUT"

    exc_res = ResourceExhaustedException("Batch size exceeded maximum allowed limit")
    assert exc_res.status_code == 413
    assert exc_res.code == "RESOURCE_EXHAUSTED"

    resp = APIErrorResponse.from_exception(
        status_code=504,
        code=exc_db.code,
        message=str(exc_db),
        path="/api/verify",
    )
    assert resp.error.code == "DATABASE_TIMEOUT"
    assert resp.error.details.get("path") == "/api/verify"
    assert len(resp.error.request_id) > 0
