"""OCR Engine Factory and Registry for GeoVerify India (Phase 7)."""

from typing import Optional, Dict
from app.config import settings
from app.document.ocr.engine import BaseOCREngine
from app.document.ocr.tesseract_engine import TesseractOCREngine
from app.document.ocr.mock_engine import MockOCREngine


def get_ocr_engine(engine_name: Optional[str] = None) -> BaseOCREngine:
    """
    Factory function resolving OCR engine:
    - 'tesseract': Force Tesseract backend
    - 'mock': Force deterministic Mock backend
    - 'auto': Use Tesseract if available on system, else fallback to Mock
    """
    target = (engine_name or settings.OCR_DEFAULT_ENGINE).lower()

    if target == "tesseract":
        return TesseractOCREngine()
    elif target == "mock":
        return MockOCREngine()
    else:  # 'auto'
        tess = TesseractOCREngine()
        if tess.is_available():
            return tess
        return MockOCREngine()
