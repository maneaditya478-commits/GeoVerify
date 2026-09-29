"""Integration tests for Document Verification API endpoints (Phase 7)."""

import pytest
import io
from PIL import Image
from httpx import AsyncClient, ASGITransport
from app.main import app


def create_test_image_bytes() -> bytes:
    img = Image.new("RGB", (600, 400), color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.mark.asyncio
async def test_api_document_verify():
    img_bytes = create_test_image_bytes()
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("address_proof.png", img_bytes, "image/png")}
        data = {"engine": "mock"}
        response = await client.post("/api/document/verify", files=files, data=data)

        assert response.status_code == 200
        json_data = response.json()
        assert "document" in json_data
        assert json_data["document"]["filename"] == "address_proof.png"
        assert "ocr" in json_data
        assert "address_extraction" in json_data
        assert "verification" in json_data
        assert len(json_data["address_candidates"]) >= 1


@pytest.mark.asyncio
async def test_api_document_extract_only():
    img_bytes = create_test_image_bytes()
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("extract_test.png", img_bytes, "image/png")}
        data = {"engine": "mock"}
        response = await client.post("/api/document/extract-only", files=files, data=data)

        assert response.status_code == 200
        json_data = response.json()
        assert json_data["document"]["filename"] == "extract_test.png"
        assert json_data["verification"] is None  # Verification was omitted


@pytest.mark.asyncio
async def test_api_document_preprocess_preview():
    img_bytes = create_test_image_bytes()
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("preview_test.png", img_bytes, "image/png")}
        response = await client.post("/api/document/preprocess-preview", files=files)

        assert response.status_code == 200
        json_data = response.json()
        assert json_data["filename"] == "preview_test.png"
        assert json_data["page_count"] == 1
        assert len(json_data["pages"]) == 1
        assert "preview_base64_jpeg" in json_data["pages"][0]
        assert "sharpness_score" in json_data["pages"][0]


@pytest.mark.asyncio
async def test_api_document_validation_failure():
    # Send non-image binary
    bad_bytes = b"NOT_AN_IMAGE_OR_PDF_FILE_CORRUPT"
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("bad.png", bad_bytes, "image/png")}
        response = await client.post("/api/document/verify", files=files)

        assert response.status_code == 400
        assert "DocumentValidationError" in response.text
