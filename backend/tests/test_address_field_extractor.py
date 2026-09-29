"""Unit tests for address region detector, field extraction, and pipeline (Phase 7)."""

import pytest
import io
from PIL import Image

from app.document.models import (
    OCRResult,
    OCRPage,
    OCRBlock,
    OCRLine,
    OCRWord,
    BoundingBox,
    DocumentAddressType,
    AddressExtractionStatus,
)
from app.document.address.region_detector import AddressRegionDetector
from app.document.address.field_extractor import AddressFieldExtractor
from app.document.address.assembler import AddressCandidateAssembler
from app.document.address.pin_recovery import PINFirstRecoveryService
from app.document.pipeline import DocumentProcessingPipeline


@pytest.fixture
def sample_ocr_result():
    lines = [
        OCRLine(
            text="Government of Maharashtra",
            confidence=0.95,
            bbox=BoundingBox(x_min=100, y_min=50, x_max=400, y_max=70),
            line_num=1,
        ),
        OCRLine(
            text="Address: Flat 402, Ganga Carnation, Near EON IT Park",
            confidence=0.92,
            bbox=BoundingBox(x_min=100, y_min=120, x_max=500, y_max=140),
            line_num=2,
        ),
        OCRLine(
            text="Kharadi, Taluka Haveli, District Pune, Maharashtra - 411014",
            confidence=0.94,
            bbox=BoundingBox(x_min=100, y_min=145, x_max=520, y_max=165),
            line_num=3,
        ),
        OCRLine(
            text="Date of Birth: 15/08/1990",
            confidence=0.98,
            bbox=BoundingBox(x_min=100, y_min=200, x_max=350, y_max=220),
            line_num=4,
        ),
    ]
    block = OCRBlock(
        lines=lines,
        text="\n".join(l.text for l in lines),
        confidence=0.94,
        bbox=BoundingBox(x_min=100, y_min=50, x_max=520, y_max=220),
        block_num=1,
    )
    page = OCRPage(
        page_num=1,
        width=800,
        height=600,
        text=block.text,
        confidence=0.94,
        blocks=[block],
        lines=lines,
    )
    return OCRResult(
        document_id="doc_test_123",
        engine="mock_ocr",
        pages=[page],
        full_text=page.text,
        mean_confidence=0.94,
        primary_language="eng",
    )


def test_region_detector_header_anchored(sample_ocr_result):
    detector = AddressRegionDetector()
    regions = detector.detect_regions(sample_ocr_result)

    assert len(regions) >= 1
    addr_reg = regions[0]
    assert addr_reg.address_type in [DocumentAddressType.PRIMARY, DocumentAddressType.RESIDENTIAL]
    assert "Kharadi" in addr_reg.full_region_text
    assert "411014" in addr_reg.full_region_text
    assert addr_reg.bbox is not None


def test_field_extractor(sample_ocr_result):
    detector = AddressRegionDetector()
    extractor = AddressFieldExtractor()

    regions = detector.detect_regions(sample_ocr_result)
    assert len(regions) > 0
    fields = extractor.extract_fields(regions[0])

    assert "pincode" in fields
    assert fields["pincode"].normalized_value == "411014"
    assert "district" in fields
    assert fields["district"].normalized_value == "Pune"
    assert "locality" in fields
    assert fields["locality"].normalized_value in ["Kharadi", "Ganga Carnation"]


def test_candidate_assembler(sample_ocr_result):
    detector = AddressRegionDetector()
    assembler = AddressCandidateAssembler()

    regions = detector.detect_regions(sample_ocr_result)
    candidates = assembler.assemble_candidates(regions)

    assert len(candidates) >= 1
    cand = candidates[0]
    assert cand.extraction_status == AddressExtractionStatus.EXTRACTED
    assert "411014" in cand.assembled_address
    assert cand.structured_components.get("pincode") == "411014"
    assert cand.structured_components.get("district") == "Pune"


@pytest.mark.asyncio
async def test_end_to_end_document_pipeline():
    pipeline = DocumentProcessingPipeline(ocr_engine_name="mock")
    
    # Create test image
    img = Image.new("RGB", (600, 400), color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    file_bytes = buf.getvalue()

    res = await pipeline.process_document(
        file_bytes=file_bytes,
        filename="test_address_proof.png",
        mime_type="image/png",
        verify_geography=True,
    )

    assert res.document.filename == "test_address_proof.png"
    assert res.ocr.status == "SUCCESS"
    assert len(res.address_candidates) >= 1
    assert res.primary_candidate is not None
    assert res.verification is not None
    assert "timings_ms" in res.model_dump() or "stage_timings_ms" in res.model_dump()
