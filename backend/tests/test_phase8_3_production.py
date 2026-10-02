"""Unit and integration tests for Phase 8.3 Production Reliability & Hardening."""

import pytest
import io
from PIL import Image
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.config import settings
from app.core.cache import (
    BoundedLRUTTLCache,
    CryptographicCacheKeyGenerator,
    verification_cache,
)
from app.core.errors import (
    APIErrorResponse,
    DatabaseTimeoutException,
    OCRTimeoutException,
    ResourceExhaustedException,
)
from app.document.validator import DocumentValidator, DocumentValidationError
from app.schemas.address import VerificationRequest
from app.verification.engine import VerificationEngine


def test_phase8_3_version_and_config():
    """Verifies that Phase 8.3 version metadata is correctly pinned."""
    assert settings.APP_VERSION == "8.3.0"
    assert settings.GEOVERIFY_CONFIG_VERSION == "8.3.0"


def test_path_traversal_sanitization_security():
    """Verifies that directory traversal filenames are safely sanitized."""
    validator = DocumentValidator()
    img = Image.new("RGB", (100, 100), color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    raw_bytes = buf.getvalue()

    malicious_names = [
        "../../../../etc/passwd.png",
        "..\\..\\system32\\cmd.exe.jpg",
        "foo/../../bar.pdf",
    ]

    for name in malicious_names:
        res = validator.validate(raw_bytes, name, "image/png")
        sanitized = res.sanitized_filename
        assert ".." not in sanitized
        assert "/" not in sanitized
        assert "\\" not in sanitized


def test_oversized_and_corrupt_file_handling():
    """Verifies immediate rejection of oversized and corrupt file payloads."""
    validator = DocumentValidator()

    # Oversized payload (> 15 MB)
    oversized = b"0" * (16 * 1024 * 1024)
    with pytest.raises(DocumentValidationError):
        validator.validate(oversized, "large.pdf", "application/pdf")

    # Corrupt truncated payload
    corrupt = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDRtruncated"
    with pytest.raises(DocumentValidationError):
        validator.validate(corrupt, "corrupt.png", "image/png")


def test_cache_version_invalidation_and_homonyms():
    """Verifies that config/data version rotation generates distinct cryptographic keys."""
    k_v82 = CryptographicCacheKeyGenerator.generate_key("Kothrud Pune", config_version="8.2.0")
    k_v83 = CryptographicCacheKeyGenerator.generate_key("Kothrud Pune", config_version="8.3.0")
    assert k_v82 != k_v83

    # Homonym isolation across states
    k_up = CryptographicCacheKeyGenerator.generate_key("Rampur", state="Uttar Pradesh", district="Rampur")
    k_bihar = CryptographicCacheKeyGenerator.generate_key("Rampur", state="Bihar", district="Gaya")
    assert k_up != k_bihar


@pytest.mark.asyncio
async def test_conservative_geographic_failure_semantics():
    """Verifies that missing or incomplete evidence never produces false verified verdicts."""
    engine = VerificationEngine()
    req = VerificationRequest(address="Random Nonexistent Place In India 999999")
    res = await engine.verify(req)
    assert res.status.value.upper() != "VERIFIED"
    assert res.score < 70
