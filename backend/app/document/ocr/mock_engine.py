"""Deterministic Mock OCR Engine for Testing and Offline Environments (Phase 7).

Generates structured OCRPage schemas with accurate bounding boxes, block hierarchies,
and word-level confidences for deterministic CI testing and synthetic benchmarks.
"""

import time
import re
from typing import Optional, List, Dict, Any
from PIL import Image

from app.document.models import OCRPage, OCRBlock, OCRLine, OCRWord, BoundingBox
from app.document.ocr.engine import BaseOCREngine
from app.document.ocr.language_detection import language_detector


class MockOCREngine(BaseOCREngine):
    """Deterministic Mock OCR engine for testing, CI pipelines, and synthetic benchmarks."""

    def __init__(self, predefined_text: Optional[str] = None, default_confidence: float = 0.94):
        self._predefined_text = predefined_text
        self._default_confidence = default_confidence

    @property
    def name(self) -> str:
        return "mock"

    def is_available(self) -> bool:
        return True

    def extract_page(
        self,
        image: Image.Image,
        page_num: int = 1,
        language: Optional[str] = None
    ) -> OCRPage:
        """
        Generates deterministic structured OCR output from synthetic image or predefined text.
        """
        t0 = time.perf_counter()
        
        # Check if text is encoded in image metadata (used for synthetic document benchmarks)
        text = self._predefined_text
        if not text and hasattr(image, "info") and "document_text" in image.info:
            text = image.info["document_text"]

        if not text:
            # Default representative mock address document
            text = (
                "MAHARASHTRA STATE ELECTRICITY DISTRIBUTION CO. LTD.\n"
                "CONSUMER BILLING RECEIPT\n"
                "Consumer No: 028491823941\n"
                "Name: ADITYA MANE\n"
                "Address: Flat 402, Ganga Carnation, Near EON IT Park, Kharadi, Pune, Maharashtra 411014\n"
                "Billing Date: 15/09/2026\n"
                "Amount: Rs. 2,450.00"
            )

        raw_lines = [l.strip() for l in text.splitlines() if l.strip()]
        lines: List[OCRLine] = []
        words: List[OCRWord] = []
        blocks: List[OCRBlock] = []

        y_offset = 80
        line_height = 35
        char_width = 12

        for l_idx, line_str in enumerate(raw_lines):
            line_num = l_idx + 1
            word_strs = line_str.split()
            x_offset = 60
            line_words: List[OCRWord] = []

            for w_idx, w_str in enumerate(word_strs):
                w_num = w_idx + 1
                w_width = max(20, len(w_str) * char_width)
                w_bbox = BoundingBox(
                    x=x_offset,
                    y=y_offset,
                    width=w_width,
                    height=line_height - 5,
                    page_num=page_num
                )
                
                # Assign confidence with slight variation
                word_conf = self._default_confidence
                if w_str.isdigit() and len(w_str) == 6:
                    word_conf = 0.98  # PIN code high confidence

                ocr_word = OCRWord(
                    text=w_str,
                    confidence=word_conf,
                    bbox=w_bbox,
                    line_num=line_num,
                    word_num=w_num,
                    page_num=page_num
                )
                line_words.append(ocr_word)
                words.append(ocr_word)
                x_offset += w_width + 10

            line_bbox = BoundingBox(
                x=60,
                y=y_offset,
                width=max(100, x_offset - 60),
                height=line_height,
                page_num=page_num
            )
            line = OCRLine(
                text=line_str,
                confidence=self._default_confidence,
                words=line_words,
                bbox=line_bbox,
                line_num=line_num,
                block_num=1,
                page_num=page_num
            )
            lines.append(line)
            y_offset += line_height + 10

        block_bbox = BoundingBox(
            x=50,
            y=70,
            width=image.width - 100 if image.width > 200 else 800,
            height=y_offset,
            page_num=page_num
        )
        block = OCRBlock(
            text="\n".join(raw_lines),
            confidence=self._default_confidence,
            lines=lines,
            bbox=block_bbox,
            block_num=1,
            page_num=page_num
        )
        blocks.append(block)

        dur_ms = round((time.perf_counter() - t0) * 1000.0, 2)

        return OCRPage(
            page_num=page_num,
            width=image.width,
            height=image.height,
            text="\n".join(raw_lines),
            confidence=self._default_confidence,
            blocks=blocks,
            lines=lines,
            words=words,
            detected_languages=language_detector.detect_languages(text),
            processing_time_ms=dur_ms
        )
