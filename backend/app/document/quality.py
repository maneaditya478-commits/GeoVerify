"""Document and OCR Quality Evaluator for GeoVerify India (Phase 7).

Evaluates:
- Sharpness / Blur metric (Laplacian variance equivalent)
- Contrast & dynamic range
- Character recognition confidence
- Address signal density
- Calibrated OCRQualityStatus (HIGH, MEDIUM, LOW, FAILED)
"""

from typing import Dict, Any, Tuple, Optional
from pydantic import BaseModel, Field
import numpy as np
from PIL import Image, ImageOps

from app.document.models import OCRQualityStatus, OCRResult, OCRPage


class QualityReport(BaseModel):
    sharpness_score: float
    contrast_score: float
    brightness_score: float
    is_blurry: bool
    is_low_contrast: bool
    width: int
    height: int
    quality_status: OCRQualityStatus = OCRQualityStatus.HIGH


class DocumentQualityEvaluator:
    """Evaluates image quality and OCR confidence metrics."""

    @classmethod
    def evaluate_image_quality(cls, image: Image.Image) -> Dict[str, Any]:
        """Calculates sharpness, contrast, and resolution metrics on input image."""
        gray = ImageOps.grayscale(image)
        np_img = np.array(gray, dtype=np.float32)

        # 1. Discrete Laplacian approximation for focus/sharpness
        if np_img.shape[0] > 3 and np_img.shape[1] > 3:
            laplacian = (
                np_img[:-2, 1:-1]
                + np_img[2:, 1:-1]
                + np_img[1:-1, :-2]
                + np_img[1:-1, 2:]
                - 4 * np_img[1:-1, 1:-1]
            )
            sharpness_var = float(np.var(laplacian))
        else:
            sharpness_var = 0.0

        # 2. Dynamic Range & Contrast
        img_min = float(np.min(np_img))
        img_max = float(np.max(np_img))
        dynamic_range = (img_max - img_min) / 255.0 if img_max > img_min else 0.0
        contrast_score = round(min(1.0, dynamic_range), 2)

        # 3. Mean Brightness
        mean_brightness = float(np.mean(np_img) / 255.0)

        # Blur and contrast threshold flags
        is_blurry = sharpness_var < 80.0
        is_low_contrast = (img_max - img_min) < 60.0

        return {
            "sharpness_var": round(sharpness_var, 2),
            "sharpness_score": round(min(1.0, sharpness_var / 500.0), 2),
            "contrast_ratio": round(dynamic_range, 2),
            "contrast_score": round(contrast_score, 2),
            "mean_brightness": round(mean_brightness, 2),
            "brightness_score": round(mean_brightness, 2),
            "is_blurry": is_blurry,
            "is_low_contrast": is_low_contrast,
            "width": image.width,
            "height": image.height,
        }

    @classmethod
    def evaluate(cls, image: Image.Image) -> QualityReport:
        """Run image quality evaluation and determine initial status."""
        metrics = cls.evaluate_image_quality(image)
        
        if metrics["is_blurry"] and metrics["is_low_contrast"]:
            status = OCRQualityStatus.LOW
        elif metrics["is_blurry"] or metrics["is_low_contrast"]:
            status = OCRQualityStatus.MEDIUM
        else:
            status = OCRQualityStatus.HIGH

        return QualityReport(
            sharpness_score=metrics["sharpness_score"],
            contrast_score=metrics["contrast_score"],
            brightness_score=metrics["brightness_score"],
            is_blurry=metrics["is_blurry"],
            is_low_contrast=metrics["is_low_contrast"],
            width=metrics["width"],
            height=metrics["height"],
            quality_status=status,
        )

    @classmethod
    def evaluate_ocr_quality(
        cls,
        ocr_result: OCRResult,
        image_quality: Optional[Dict[str, Any]] = None,
    ) -> OCRQualityStatus:
        """Determines calibrated OCRQualityStatus from text confidence, character count, and image metrics."""
        if not ocr_result.pages or len(ocr_result.full_text.strip()) == 0:
            return OCRQualityStatus.FAILED

        conf = ocr_result.mean_confidence
        text_len = len(ocr_result.full_text.strip())

        if text_len < 10 or conf < 0.30:
            return OCRQualityStatus.LOW
        elif conf >= 0.80 and text_len >= 25:
            return OCRQualityStatus.HIGH
        elif conf >= 0.55:
            return OCRQualityStatus.MEDIUM
        else:
            return OCRQualityStatus.LOW


document_quality_evaluator = DocumentQualityEvaluator()
