"""Configurable Image Preprocessor for Indian Document OCR (Phase 7).

Applies controlled computer vision transformations:
- Grayscale & Contrast Normalization
- Denoising & Median Filtering
- Deskew & Orientation Correction
- Adaptive Binarization / Thresholding
- DPI / Resolution Normalization
"""

import math
from typing import Tuple, List, Dict, Any, Optional
import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageEnhance


class PreprocessedImageResult:
    """Encapsulates preprocessed PIL image and applied transformation metadata."""
    def __init__(self, image: Image.Image, operations_applied: List[str], rotation_deg: float = 0.0):
        self.image = image
        self.operations_applied = operations_applied
        self.rotation_deg = rotation_deg

    def __iter__(self):
        yield self.image
        yield self.rotation_deg


class ImagePreprocessor:
    """Preprocesses document images to optimize OCR character recognition rates."""

    @classmethod
    def preprocess(
        cls,
        image: Image.Image,
        enable_deskew: bool = True,
        enable_contrast: bool = True,
        enable_denoise: bool = True,
        enable_binarization: bool = False,
        target_min_dpi_width: int = 1500
    ) -> PreprocessedImageResult:
        """
        Executes controlled preprocessing pipeline while preserving the original image.
        """
        operations: List[str] = []
        proc = image.copy()

        # 1. Convert to Grayscale
        if proc.mode != "L":
            proc = ImageOps.grayscale(proc)
            operations.append("GRAYSCALE")

        # 2. Resolution Normalization (Upscale low-res scans to improve OCR)
        w, h = proc.size
        if w < target_min_dpi_width:
            scale = target_min_dpi_width / float(w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            proc = proc.resize((new_w, new_h), Image.Resampling.BICUBIC)
            operations.append(f"RESIZE_{w}x{h}_TO_{new_w}x{new_h}")

        # 3. Contrast & Histogram Equalization
        if enable_contrast:
            # Contrast enhancement
            enhancer = ImageEnhance.Contrast(proc)
            proc = enhancer.enhance(1.4)
            operations.append("CONTRAST_ENHANCE_1.4")

        # 4. Denoising / Median Filter for salt-and-pepper scan noise
        if enable_denoise:
            proc = proc.filter(ImageFilter.MedianFilter(size=3))
            operations.append("MEDIAN_FILTER_3x3")

        # 5. Deskew / Orientation Correction
        deskew_deg = 0.0
        if enable_deskew:
            deskew_deg = cls.detect_skew_angle(proc)
            if abs(deskew_deg) > 0.5:
                # Rotate with white background fill
                proc = proc.rotate(-deskew_deg, expand=True, fillcolor=255)
                operations.append(f"DESKEW_{deskew_deg:.2f}_DEG")

        # 6. Adaptive Thresholding / Binarization (Optional)
        if enable_binarization:
            # Otsu threshold approximation via numpy
            np_img = np.array(proc)
            thresh = int(np.mean(np_img) * 0.9)
            proc = Image.fromarray((np_img > thresh).astype(np.uint8) * 255)
            operations.append(f"BINARIZE_THRESH_{thresh}")

        return PreprocessedImageResult(
            image=proc,
            operations_applied=operations,
            rotation_deg=deskew_deg
        )

    @classmethod
    def detect_skew_angle(cls, gray_image: Image.Image) -> float:
        """
        Estimates skew angle of text lines using projection profile variance.
        Bounds search space to [-15°, +15°].
        """
        # Downsample for faster projection profiling
        thumb = gray_image.copy()
        thumb.thumbnail((600, 600))
        np_img = 255 - np.array(thumb, dtype=np.uint8)  # Invert so text is foreground (bright)

        best_angle = 0.0
        max_variance = -1.0

        # Scan angles from -15 to +15 in 0.5 degree steps
        for angle in np.arange(-15.0, 15.5, 0.5):
            # Rotate inverted thumbnail
            rot_img = Image.fromarray(np_img).rotate(angle, expand=False, fillcolor=0)
            rot_arr = np.array(rot_img)
            
            # Horizontal projection (sum along columns)
            proj = np.sum(rot_arr, axis=1)
            # Compute variance of projection (sharp peaks when text is horizontally aligned)
            var = np.var(proj)

            if var > max_variance:
                max_variance = var
                best_angle = float(angle)

        return best_angle


image_preprocessor = ImagePreprocessor()
