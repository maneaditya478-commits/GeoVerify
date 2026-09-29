"""Domain models, enums, and dataclasses for Phase 7 Document & OCR Address Extraction."""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, model_validator


class DocumentType(str, Enum):
    IMAGE = "image"
    PDF = "pdf"
    IMAGE_PNG = "image/png"
    IMAGE_JPEG = "image/jpeg"
    IMAGE_WEBP = "image/webp"


class OCRQualityStatus(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    FAILED = "FAILED"


class AddressExtractionStatus(str, Enum):
    EXTRACTED = "EXTRACTED"
    PARTIAL = "PARTIAL"
    PARTIALLY_EXTRACTED = "PARTIALLY_EXTRACTED"
    AMBIGUOUS = "AMBIGUOUS"
    NOT_FOUND = "NOT_FOUND"
    FAILED = "FAILED"


class ExtractionMethod(str, Enum):
    EXPLICIT = "EXPLICIT"
    PIN_RECOVERY = "PIN_RECOVERY"
    ADMIN_CONTEXT_RECOVERY = "ADMIN_CONTEXT_RECOVERY"
    OCR_REPAIRED = "OCR_REPAIRED"
    INFERRED = "INFERRED"


class DocumentAddressType(str, Enum):
    PRIMARY = "PRIMARY"
    RESIDENTIAL = "RESIDENTIAL"
    PERMANENT = "PERMANENT"
    CURRENT = "CURRENT"
    CORRESPONDENCE = "CORRESPONDENCE"
    OFFICE = "OFFICE"
    REGISTERED = "REGISTERED"
    BILLING = "BILLING"
    SHIPPING = "SHIPPING"
    UNKNOWN = "UNKNOWN"


class BoundingBox(BaseModel):
    """Normalized or pixel bounding box supporting (x, y, width, height) or (x_min, y_min, x_max, y_max)."""
    x: int = Field(0, description="Left coordinate in pixels")
    y: int = Field(0, description="Top coordinate in pixels")
    width: int = Field(0, description="Width in pixels")
    height: int = Field(0, description="Height in pixels")
    page_num: int = Field(1, description="1-indexed document page number")

    @model_validator(mode="before")
    @classmethod
    def convert_min_max_to_xywh(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "x_min" in data and "y_min" in data and "x_max" in data and "y_max" in data:
                x_min = int(data["x_min"])
                y_min = int(data["y_min"])
                x_max = int(data["x_max"])
                y_max = int(data["y_max"])
                data["x"] = x_min
                data["y"] = y_min
                data["width"] = max(0, x_max - x_min)
                data["height"] = max(0, y_max - y_min)
        return data

    @property
    def x_min(self) -> int:
        return self.x

    @property
    def y_min(self) -> int:
        return self.y

    @property
    def x_max(self) -> int:
        return self.x + self.width

    @property
    def y_max(self) -> int:
        return self.y + self.height


class OCRWord(BaseModel):
    text: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox: Optional[BoundingBox] = None
    line_num: int = 1
    word_num: int = 1
    page_num: int = 1
    language: Optional[str] = None


class OCRLine(BaseModel):
    text: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    words: List[OCRWord] = Field(default_factory=list)
    bbox: Optional[BoundingBox] = None
    line_num: int = 1
    block_num: int = 1
    page_num: int = 1
    language: Optional[str] = None


class OCRBlock(BaseModel):
    text: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    lines: List[OCRLine] = Field(default_factory=list)
    bbox: Optional[BoundingBox] = None
    block_num: int = 1
    page_num: int = 1


class OCRPage(BaseModel):
    page_num: int = 1
    width: int = 0
    height: int = 0
    text: str = ""
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    blocks: List[OCRBlock] = Field(default_factory=list)
    lines: List[OCRLine] = Field(default_factory=list)
    words: List[OCRWord] = Field(default_factory=list)
    detected_languages: Dict[str, float] = Field(default_factory=dict)
    processing_time_ms: float = 0.0


class OCRResult(BaseModel):
    document_id: str
    engine: str
    pages: List[OCRPage] = Field(default_factory=list)
    full_text: str = ""
    mean_confidence: float = Field(0.0, ge=0.0, le=1.0)
    primary_language: str = "eng"
    quality_status: OCRQualityStatus = OCRQualityStatus.HIGH
    processing_time_ms: float = 0.0


class AddressRegion(BaseModel):
    """Detected address region / bounding box within an OCR document."""
    region_id: str
    address_type: DocumentAddressType = DocumentAddressType.UNKNOWN
    page_num: int = 1
    bbox: Optional[BoundingBox] = None
    raw_lines: List[str] = Field(default_factory=list)
    full_region_text: str = ""
    header_keyword_detected: Optional[str] = None
    confidence: float = Field(0.0, ge=0.0, le=1.0)


class ExtractedAddressField(BaseModel):
    field_name: str
    raw_value: str
    normalized_value: Optional[str] = None
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    extraction_method: ExtractionMethod = ExtractionMethod.EXPLICIT
    line_num: Optional[int] = None
    page_num: Optional[int] = 1
    bbox: Optional[BoundingBox] = None
    source_text: Optional[str] = None
    correction_reason: Optional[str] = None


class ExtractedAddressCandidate(BaseModel):
    """Structured address extracted from document with provenance."""
    candidate_id: str
    address_type: DocumentAddressType = DocumentAddressType.UNKNOWN
    raw_address_text: str
    assembled_address: str
    fields: Dict[str, ExtractedAddressField] = Field(default_factory=dict)
    structured_components: Dict[str, Optional[str]] = Field(default_factory=dict)
    extraction_confidence: float = Field(0.0, ge=0.0, le=1.0)
    extraction_status: AddressExtractionStatus = AddressExtractionStatus.EXTRACTED
    page_num: int = 1
    region_bbox: Optional[BoundingBox] = None
    provenance: Dict[str, Any] = Field(default_factory=dict)
    pin_recovered: bool = False
    verification_result: Optional[Any] = None  # VerificationResponse attached dynamically
