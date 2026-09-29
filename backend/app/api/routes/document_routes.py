"""Document verification API routes (Phase 7).

Endpoints for:
- POST /api/document/verify: Upload document, perform OCR, extract address, and verify geographic consistency.
- POST /api/document/extract-only: OCR + address extraction without geographic verification.
- POST /api/document/preprocess-preview: Inspection of preprocessing steps (deskew, quality, contrast).
"""

import base64
import io
from typing import Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel

from app.document.pipeline import DocumentProcessingPipeline
from app.document.validator import DocumentValidator, DocumentValidationError
from app.document.loader import DocumentLoader
from app.document.image_preprocessor import ImagePreprocessor
from app.document.quality import DocumentQualityEvaluator
from app.schemas.document import DocumentVerificationResponse

router = APIRouter(prefix="/document", tags=["Document Address Verification"])
pipeline = DocumentProcessingPipeline()
validator = DocumentValidator()
loader = DocumentLoader()
preprocessor = ImagePreprocessor()
quality_evaluator = DocumentQualityEvaluator()


@router.post(
    "/verify",
    response_model=DocumentVerificationResponse,
    summary="Upload document for OCR address extraction and geographic verification",
    description="Accepts PDF or image files (JPEG, PNG, WebP), extracts text via OCR, segments candidate address blocks, repairs OCR artifacts, and verifies geographic consistency.",
)
async def verify_document(
    file: UploadFile = File(..., description="Document file (PDF, PNG, JPEG, WebP)"),
    engine: Optional[str] = Form("auto", description="OCR engine ('auto', 'tesseract', 'mock')"),
):
    """Upload document, perform OCR, extract address candidate, and verify against Indian administrative reference datasets."""
    try:
        content = await file.read()
        response = await pipeline.process_document(
            file_bytes=content,
            filename=file.filename or "document.png",
            mime_type=file.content_type,
            verify_geography=True,
            engine_override=engine,
        )
        return response
    except DocumentValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "DocumentValidationError", "message": str(e)},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "DocumentProcessingError", "message": str(e)},
        )


@router.post(
    "/extract-only",
    response_model=DocumentVerificationResponse,
    summary="Extract address from document without geographic verification",
)
async def extract_only_document(
    file: UploadFile = File(..., description="Document file"),
    engine: Optional[str] = Form("auto", description="OCR engine"),
):
    """Extract address text, bounding boxes, and structured components without executing geographic verification."""
    try:
        content = await file.read()
        response = await pipeline.process_document(
            file_bytes=content,
            filename=file.filename or "document.png",
            mime_type=file.content_type,
            verify_geography=False,
            engine_override=engine,
        )
        return response
    except DocumentValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "DocumentValidationError", "message": str(e)},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "DocumentProcessingError", "message": str(e)},
        )


@router.post(
    "/preprocess-preview",
    summary="Preview document preprocessing and quality diagnostics",
)
async def preprocess_preview(
    file: UploadFile = File(..., description="Document file to inspect"),
):
    """Returns preprocessing diagnostics, deskew angle, and quality metrics."""
    try:
        content = await file.read()
        validation_res = validator.validate(content, file.filename or "doc.png", file.content_type)
        images = loader.load_pages(content, validation_res.detected_type)
        
        pages_preview = []
        for idx, page_item in enumerate(images, start=1):
            img = page_item.image if hasattr(page_item, "image") else page_item
            quality = quality_evaluator.evaluate(img)
            prep_res = preprocessor.preprocess(img)
            prep_img = prep_res.image
            deskew_angle = prep_res.rotation_deg

            # Create small thumbnail preview
            thumb = prep_img.copy()
            thumb.thumbnail((400, 400))
            buffer = io.BytesIO()
            thumb.save(buffer, format="JPEG", quality=70)
            thumb_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

            pages_preview.append({
                "page_num": idx,
                "original_dimensions": {"width": img.width, "height": img.height},
                "deskew_angle_degrees": deskew_angle,
                "quality_status": quality.quality_status.value,
                "sharpness_score": quality.sharpness_score,
                "contrast_score": quality.contrast_score,
                "brightness_score": quality.brightness_score,
                "preview_base64_jpeg": f"data:image/jpeg;base64,{thumb_b64}",
            })

        return {
            "filename": validation_res.sanitized_filename,
            "file_type": validation_res.detected_type.value,
            "page_count": len(images),
            "pages": pages_preview,
        }
    except DocumentValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "DocumentValidationError", "message": str(e)},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "PreprocessPreviewError", "message": str(e)},
        )
