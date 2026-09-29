"""Unit tests for document validator and security filters (Phase 7)."""

import pytest
import io
from PIL import Image
import pypdf

from app.document.validator import DocumentValidator, DocumentValidationError
from app.document.models import DocumentType


@pytest.fixture
def validator():
    return DocumentValidator()


def create_test_image_bytes(format="PNG", size=(200, 200), color="white") -> bytes:
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


def create_valid_pdf_bytes() -> bytes:
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_validator_png_image(validator):
    data = create_test_image_bytes(format="PNG")
    res = validator.validate(data, "aadhaar_card.png", "image/png")
    assert res.is_valid is True
    assert res.detected_type in [DocumentType.IMAGE, DocumentType.IMAGE_PNG]
    assert res.sanitized_filename == "aadhaar_card.png"
    assert len(res.sha256) == 64


def test_validator_jpeg_image(validator):
    data = create_test_image_bytes(format="JPEG")
    res = validator.validate(data, "voter_id.jpg", "image/jpeg")
    assert res.is_valid is True
    assert res.detected_type in [DocumentType.IMAGE, DocumentType.IMAGE_JPEG]


def test_validator_webp_image(validator):
    data = create_test_image_bytes(format="WEBP")
    res = validator.validate(data, "utility_bill.webp", "image/webp")
    assert res.is_valid is True
    assert res.detected_type in [DocumentType.IMAGE, DocumentType.IMAGE_WEBP]


def test_validator_pdf(validator):
    pdf_bytes = create_valid_pdf_bytes()
    res = validator.validate(pdf_bytes, "rent_agreement.pdf", "application/pdf")
    assert res.is_valid is True
    assert res.detected_type == DocumentType.PDF
    assert res.page_count == 1


def test_validator_rejects_empty_file(validator):
    with pytest.raises(DocumentValidationError, match="empty"):
        validator.validate(b"", "empty.png")


def test_validator_rejects_path_traversal(validator):
    data = create_test_image_bytes(format="PNG")
    res = validator.validate(data, "../../../etc/passwd.png")
    assert ".." not in res.sanitized_filename
    assert res.sanitized_filename == "passwd.png"


def test_validator_rejects_invalid_magic_bytes(validator):
    bad_data = b"EXECUTABLE_BINARY_DATA_NOT_AN_IMAGE_OR_PDF"
    with pytest.raises(DocumentValidationError, match="File header signature"):
        validator.validate(bad_data, "malicious.png")


def test_validator_rejects_oversized_file(validator):
    # 16 MB fake header
    oversized = b"\x89PNG\r\n\x1a\n" + b"\x00" * (16 * 1024 * 1024)
    with pytest.raises(DocumentValidationError, match="exceeds maximum"):
        validator.validate(oversized, "large.png")
