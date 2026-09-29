"""Secure Document Validator for GeoVerify India (Phase 7).

Validates:
- File signatures (magic bytes for JPEG, PNG, WEBP, PDF)
- Allowed MIME types and file extensions
- File size thresholds (configurable)
- Image dimensions & PDF page count limits
- Corrupted or zero-byte file detection
- Filename sanitization & path traversal prevention
"""

import io
import re
import os
import hashlib
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
from pydantic import BaseModel
from PIL import Image, ImageOps
import pypdf

from app.config import settings
from app.document.models import DocumentType


# Magic byte signatures
MAGIC_BYTES = {
    "jpeg": b"\xFF\xD8\xFF",
    "png": b"\x89PNG\r\n\x1a\n",
    "webp": b"RIFF",
    "pdf": b"%PDF-"
}


class DocumentValidationError(Exception):
    """Raised when document validation fails."""
    def __init__(self, code: str, message: str, status_code: int = 400):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class DocumentValidationResult(BaseModel):
    is_valid: bool = True
    detected_type: DocumentType
    sanitized_filename: str
    mime_type: str
    size_bytes: int
    page_count: int = 1
    width: int = 0
    height: int = 0
    sha256: str


class DocumentValidator:
    """Validates untrusted user document uploads before processing."""

    @staticmethod
    def sanitize_filename(filename: Optional[str]) -> str:
        """Sanitizes user filename and protects against path traversal."""
        if not filename:
            return "unnamed_document.png"
        
        # Remove directories/path traversal
        clean = Path(filename).name
        # Keep alphanumeric, underscores, hyphens, and dots
        clean = re.sub(r"[^\w\-.]", "_", clean)
        # Avoid leading dots or empty
        clean = clean.lstrip(".")
        return clean or "document.png"

    @classmethod
    def validate_file(
        cls,
        file_bytes: bytes,
        filename: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validates file integrity, magic bytes, dimensions, and limits."""
        res = cls.validate(file_bytes, filename, content_type)
        return {
            "filename": res.sanitized_filename,
            "file_type": res.detected_type,
            "mime_type": res.mime_type,
            "size_bytes": res.size_bytes,
            "page_count": res.page_count,
            "width": res.width,
            "height": res.height,
            "sha256": res.sha256
        }

    @classmethod
    def validate(
        cls,
        file_bytes: bytes,
        filename: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> DocumentValidationResult:
        """Validates file integrity, magic bytes, dimensions, and limits and returns structured result."""
        if not file_bytes or len(file_bytes) == 0:
            raise DocumentValidationError("EMPTY_FILE", "Uploaded document is empty (0 bytes).")

        size_bytes = len(file_bytes)
        max_bytes = settings.MAX_DOCUMENT_SIZE_MB * 1024 * 1024
        if size_bytes > max_bytes:
            raise DocumentValidationError(
                "FILE_TOO_LARGE",
                f"File size ({size_bytes / (1024*1024):.2f} MB) exceeds maximum allowed limit ({settings.MAX_DOCUMENT_SIZE_MB} MB)."
            )

        sanitized_name = cls.sanitize_filename(filename)
        ext = Path(sanitized_name).suffix.lower()

        if ext not in settings.ALLOWED_DOCUMENT_EXTENSIONS:
            raise DocumentValidationError(
                "UNSUPPORTED_EXTENSION",
                f"File extension '{ext}' is not supported. Allowed extensions: {', '.join(settings.ALLOWED_DOCUMENT_EXTENSIONS)}"
            )

        # Detect and verify magic bytes
        doc_type, mime_type = cls._detect_file_signature(file_bytes, ext)

        page_count = 1
        width = 0
        height = 0

        if doc_type == DocumentType.IMAGE:
            try:
                with Image.open(io.BytesIO(file_bytes)) as img:
                    img.verify()
                # Re-open for dimension inspection after verify()
                with Image.open(io.BytesIO(file_bytes)) as img:
                    width, height = img.size
                    if width > settings.MAX_IMAGE_WIDTH or height > settings.MAX_IMAGE_HEIGHT:
                        raise DocumentValidationError(
                            "IMAGE_DIMENSIONS_EXCEEDED",
                            f"Image dimensions ({width}x{height}) exceed maximum allowed ({settings.MAX_IMAGE_WIDTH}x{settings.MAX_IMAGE_HEIGHT})."
                        )
                    if width < 50 or height < 50:
                        raise DocumentValidationError(
                            "IMAGE_TOO_SMALL",
                            f"Image dimensions ({width}x{height}) are too small for OCR processing."
                        )
            except DocumentValidationError:
                raise
            except Exception as e:
                raise DocumentValidationError("CORRUPTED_IMAGE", f"Corrupted or invalid image file: {str(e)}")

        elif doc_type == DocumentType.PDF:
            try:
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                page_count = len(reader.pages)
                if page_count == 0:
                    raise DocumentValidationError("EMPTY_PDF", "PDF document contains 0 pages.")
                if page_count > settings.MAX_DOCUMENT_PAGES:
                    raise DocumentValidationError(
                        "PAGE_LIMIT_EXCEEDED",
                        f"PDF page count ({page_count}) exceeds maximum allowed ({settings.MAX_DOCUMENT_PAGES} pages)."
                    )
            except DocumentValidationError:
                raise
            except Exception as e:
                raise DocumentValidationError("CORRUPTED_PDF", f"Corrupted or password-protected PDF document: {str(e)}")

        sha256 = hashlib.sha256(file_bytes).hexdigest()

        return DocumentValidationResult(
            is_valid=True,
            detected_type=doc_type,
            sanitized_filename=sanitized_name,
            mime_type=mime_type,
            size_bytes=size_bytes,
            page_count=page_count,
            width=width,
            height=height,
            sha256=sha256
        )

    @staticmethod
    def _detect_file_signature(file_bytes: bytes, ext: str) -> Tuple[DocumentType, str]:
        """Validates magic bytes against declared file type."""
        header = file_bytes[:16]

        if header.startswith(MAGIC_BYTES["jpeg"]):
            return DocumentType.IMAGE, "image/jpeg"
        elif header.startswith(MAGIC_BYTES["png"]):
            return DocumentType.IMAGE, "image/png"
        elif header.startswith(MAGIC_BYTES["webp"]) and b"WEBP" in file_bytes[:16]:
            return DocumentType.IMAGE, "image/webp"
        elif header.startswith(MAGIC_BYTES["pdf"]):
            return DocumentType.PDF, "application/pdf"
        
        # Fallback check for extensions if partial header match
        if ext in [".jpg", ".jpeg"] and (header.startswith(b"\xFF\xD8")):
            return DocumentType.IMAGE, "image/jpeg"
        elif ext == ".pdf" and b"%PDF" in file_bytes[:1024]:
            return DocumentType.PDF, "application/pdf"

        raise DocumentValidationError(
            "MAGIC_BYTE_MISMATCH",
            "File header signature does not match supported image or PDF formats."
        )


document_validator = DocumentValidator()
