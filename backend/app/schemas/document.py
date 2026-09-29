"""Public API Pydantic schemas for Document-based Address Verification (Phase 7)."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.document.models import (
    DocumentType,
    OCRQualityStatus,
    AddressExtractionStatus,
    DocumentAddressType,
    ExtractedAddressCandidate,
    OCRResult
)
from app.schemas.verification import VerificationResponse


class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    file_type: DocumentType
    mime_type: str
    size_bytes: int
    page_count: int
    sha256: str


class OCRMetadata(BaseModel):
    status: str = "SUCCESS"  # SUCCESS, LOW_CONFIDENCE, FAILED
    engine: str = "auto"
    mean_confidence: float = 0.0
    quality_status: OCRQualityStatus = OCRQualityStatus.HIGH
    primary_language: str = "eng"
    languages_detected: Dict[str, float] = Field(default_factory=dict)
    pages_processed: int = 1
    processing_time_ms: float = 0.0
    ocr_result: Optional[OCRResult] = None


class AddressExtractionMetadata(BaseModel):
    status: AddressExtractionStatus = AddressExtractionStatus.EXTRACTED
    extraction_confidence: float = 0.0
    total_candidates_found: int = 1
    selected_candidate_index: int = 0
    extracted_fields_count: int = 0
    pin_recovered: bool = False
    processing_time_ms: float = 0.0


class DocumentVerificationResponse(BaseModel):
    """Unified response for POST /api/document/verify."""
    document: DocumentMetadata
    ocr: OCRMetadata
    address_extraction: AddressExtractionMetadata
    address_candidates: List[ExtractedAddressCandidate] = Field(default_factory=list)
    primary_candidate: Optional[ExtractedAddressCandidate] = None
    verification: Optional[VerificationResponse] = None  # Full GeoVerify geographic verification
    transformation_pipeline: List[Dict[str, Any]] = Field(default_factory=list)
    stage_timings_ms: Dict[str, float] = Field(default_factory=dict)
    summary: str = ""
