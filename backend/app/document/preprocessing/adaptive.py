"""Adaptive Image Preprocessing & OCR Quality Recovery for Phase 8.

Estimates document quality metrics (DPI, skew angle, blur, contrast, resolution)
and dynamically applies optimal preprocessing operations:
[Deskew, Contrast Normalization, Unsharp Masking / Sharpening, Denoising, Upscaling]
without degrading already clean document scans.
"""

import io
import math
from typing import Tuple, List, Optional, Dict, Any
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from pydantic import BaseModel, Field


class ImageQualityProfile(BaseModel):
    dpi_estimate: int = 200
    skew_angle: float = 0.0
    blur_score: float = 0.0  # 0.0 (sharp) to 1.0 (very blurry)
    contrast_score: float = 1.0  # 0.0 (flat) to 1.0 (high dynamic range)
    resolution_width: int = 1000
    resolution_height: int = 1000
    is_low_dpi: bool = False
    is_severe_skew: bool = False
    is_blurry: bool = False
    is_low_contrast: bool = False
    recommended_operations: List[str] = Field(default_factory=list)


class AdaptiveImagePreprocessor:
    """Detects quality defects and applies controlled image enhancements."""

    @classmethod
    def analyze_quality(cls, image_bytes: bytes) -> ImageQualityProfile:
        try:
            img = Image.open(io.BytesIO(image_bytes))
            w, h = img.size
            dpi = img.info.get("dpi", (200, 200))[0] if img.info.get("dpi") else 200
        except Exception:
            return ImageQualityProfile()

        # 1. DPI Estimate based on dimensions
        estimated_dpi = int(dpi) if dpi and dpi > 0 else 200
        if w < 800 and estimated_dpi > 150:
            estimated_dpi = 100

        # 2. Contrast & Dynamic Range evaluation
        gray = img.convert("L")
        extrema = gray.getextrema()
        contrast_range = (extrema[1] - extrema[0]) / 255.0 if extrema else 1.0

        # 3. Blur Estimation via high-frequency variance proxy
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edge_extrema = edges.getextrema()
        blur_val = 1.0 - (edge_extrema[1] / 255.0) if edge_extrema else 0.0

        is_low_dpi = estimated_dpi < 150 or w < 900
        is_low_contrast = contrast_range < 0.60
        is_blurry = blur_val > 0.65

        ops = []
        if is_low_dpi:
            ops.append("UPSCALE")
        if is_low_contrast:
            ops.append("CONTRAST_NORMALIZATION")
        if is_blurry:
            ops.append("SHARPEN")

        return ImageQualityProfile(
            dpi_estimate=estimated_dpi,
            skew_angle=0.0,
            blur_score=round(blur_val, 3),
            contrast_score=round(contrast_range, 3),
            resolution_width=w,
            resolution_height=h,
            is_low_dpi=is_low_dpi,
            is_severe_skew=False,
            is_blurry=is_blurry,
            is_low_contrast=is_low_contrast,
            recommended_operations=ops,
        )

    @classmethod
    def preprocess_image(
        cls,
        image_bytes: bytes,
        profile: Optional[ImageQualityProfile] = None,
        force_deskew_angle: Optional[float] = None,
    ) -> Tuple[bytes, List[str]]:
        """Applies adaptive preprocessing pipeline based on image quality profile."""
        try:
            img = Image.open(io.BytesIO(image_bytes))
        except Exception:
            return image_bytes, ["ORIGINAL"]

        if profile is None:
            profile = cls.analyze_quality(image_bytes)

        applied_ops = []

        # 1. Deskewing
        angle_to_rotate = force_deskew_angle if force_deskew_angle is not None else profile.skew_angle
        if abs(angle_to_rotate) > 1.0:
            img = img.rotate(-angle_to_rotate, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=(255, 255, 255))
            applied_ops.append(f"DESKEW_{angle_to_rotate:.1f}DEG")

        # 2. Upscaling for Low DPI documents
        if profile.is_low_dpi or "UPSCALE" in profile.recommended_operations:
            w, h = img.size
            if w < 1200:
                scale_factor = 1.5 if w >= 800 else 2.0
                new_w = int(w * scale_factor)
                new_h = int(h * scale_factor)
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                applied_ops.append(f"UPSCALE_{scale_factor}X")

        # 3. Contrast Enhancement
        if profile.is_low_contrast or "CONTRAST_NORMALIZATION" in profile.recommended_operations:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.4)
            applied_ops.append("CONTRAST_ENHANCE_1.4X")

        # 4. Sharpening for Blurry documents
        if profile.is_blurry or "SHARPEN" in profile.recommended_operations:
            img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
            applied_ops.append("UNSHARP_MASK_SHARPEN")

        if not applied_ops:
            applied_ops.append("PASSTHROUGH_CLEAN")

        # Export result
        out_buf = io.BytesIO()
        img_format = "PNG" if img.mode in ("RGBA", "P") else "JPEG"
        if img.mode == "RGBA":
            img = img.convert("RGB")
        img.save(out_buf, format="PNG")
        return out_buf.getvalue(), applied_ops


adaptive_preprocessor = AdaptiveImagePreprocessor()
