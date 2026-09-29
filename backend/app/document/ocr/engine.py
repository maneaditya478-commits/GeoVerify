"""Abstract Base Interface for OCR Engines (Phase 7).

Decouples GeoVerify India from specific OCR backends (Tesseract, PaddleOCR, EasyOCR, Mock, Vision-LLM).
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from PIL import Image

from app.document.models import OCRPage, OCRResult


class BaseOCREngine(ABC):
    """Abstract interface for all OCR engine backends."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the unique engine identifier name."""
        pass

    @property
    def engine_name(self) -> str:
        """Alias for engine identifier name."""
        return self.name

    @abstractmethod
    def is_available(self) -> bool:
        """Checks if required binaries/libraries for this engine are available."""
        pass

    @abstractmethod
    def extract_page(
        self,
        image: Image.Image,
        page_num: int = 1,
        language: Optional[str] = None
    ) -> OCRPage:
        """
        Extracts structured text, bounding boxes, words, lines, and confidences from a single page image.
        """
        pass

    def process_page(
        self,
        image: Image.Image,
        page_num: int = 1,
        language: Optional[str] = None
    ) -> OCRPage:
        """Alias for extract_page."""
        return self.extract_page(image, page_num=page_num, language=language)
