"""Tesseract OCR Engine Backend for GeoVerify India (Phase 7).

Extracts spatial bounding boxes, block hierarchy, line structures, word-level confidences,
and multilingual Indic characters using pytesseract.
"""

import shutil
import time
from typing import Optional, List, Dict, Any
from PIL import Image
import pytesseract
from pytesseract import Output

from app.config import settings
from app.document.models import OCRPage, OCRBlock, OCRLine, OCRWord, BoundingBox
from app.document.ocr.engine import BaseOCREngine
from app.document.ocr.language_detection import language_detector


class TesseractOCREngine(BaseOCREngine):
    """Production Tesseract OCR Engine wrapper with structured spatial extraction."""

    def __init__(self, tesseract_cmd: Optional[str] = None):
        self._custom_cmd = tesseract_cmd
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    @property
    def name(self) -> str:
        return "tesseract"

    def is_available(self) -> bool:
        """Checks if tesseract executable is accessible in PATH."""
        return shutil.which(pytesseract.pytesseract.tesseract_cmd or "tesseract") is not None

    def extract_page(
        self,
        image: Image.Image,
        page_num: int = 1,
        language: Optional[str] = None
    ) -> OCRPage:
        """
        Executes Tesseract OCR and parses detailed TSV/dict output into OCRPage schema.
        """
        t0 = time.perf_counter()
        lang = language or settings.OCR_DEFAULT_LANGUAGES

        # If tesseract is not available on host system, raise exception so caller can fallback to mock/alternative
        if not self.is_available():
            raise RuntimeError("Tesseract binary not found in system PATH. Install Tesseract or use Mock/Auto engine.")

        data = pytesseract.image_to_data(
            image,
            lang=lang,
            output_type=Output.DICT,
            config="--psm 3"
        )

        n_boxes = len(data["text"])
        words: List[OCRWord] = []
        lines_dict: Dict[Tuple[int, int], List[OCRWord]] = {}
        blocks_dict: Dict[int, List[OCRLine]] = {}

        for i in range(n_boxes):
            raw_txt = data["text"][i].strip()
            conf_val = float(data["conf"][i])
            if not raw_txt or conf_val < 0:
                continue

            conf = round(conf_val / 100.0, 3)
            x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
            block_num = data["block_num"][i]
            line_num = data["line_num"][i]
            word_num = data["word_num"][i]

            bbox = BoundingBox(x=x, y=y, width=w, height=h, page_num=page_num)
            word = OCRWord(
                text=raw_txt,
                confidence=conf,
                bbox=bbox,
                line_num=line_num,
                word_num=word_num,
                page_num=page_num
            )
            words.append(word)
            lines_dict.setdefault((block_num, line_num), []).append(word)

        # Assemble Lines
        assembled_lines: List[OCRLine] = []
        for (b_num, l_num), w_list in sorted(lines_dict.items()):
            line_text = " ".join(w.text for w in w_list)
            mean_conf = sum(w.confidence for w in w_list) / len(w_list) if w_list else 0.0
            
            # Compute line bounding box envelope
            min_x = min(w.bbox.x for w in w_list if w.bbox)
            min_y = min(w.bbox.y for w in w_list if w.bbox)
            max_x = max(w.bbox.x + w.bbox.width for w in w_list if w.bbox)
            max_y = max(w.bbox.y + w.bbox.height for w in w_list if w.bbox)
            line_bbox = BoundingBox(x=min_x, y=min_y, width=max_x - min_x, height=max_y - min_y, page_num=page_num)

            line = OCRLine(
                text=line_text,
                confidence=round(mean_conf, 3),
                words=w_list,
                bbox=line_bbox,
                line_num=l_num,
                block_num=b_num,
                page_num=page_num
            )
            assembled_lines.append(line)
            blocks_dict.setdefault(b_num, []).append(line)

        # Assemble Blocks
        assembled_blocks: List[OCRBlock] = []
        for b_num, l_list in sorted(blocks_dict.items()):
            block_text = "\n".join(l.text for l in l_list)
            mean_conf = sum(l.confidence for l in l_list) / len(l_list) if l_list else 0.0
            min_x = min(l.bbox.x for l in l_list if l.bbox)
            min_y = min(l.bbox.y for l in l_list if l.bbox)
            max_x = max(l.bbox.x + l.bbox.width for l in l_list if l.bbox)
            max_y = max(l.bbox.y + l.bbox.height for l in l_list if l.bbox)
            block_bbox = BoundingBox(x=min_x, y=min_y, width=max_x - min_x, height=max_y - min_y, page_num=page_num)

            assembled_blocks.append(OCRBlock(
                text=block_text,
                confidence=round(mean_conf, 3),
                lines=l_list,
                bbox=block_bbox,
                block_num=b_num,
                page_num=page_num
            ))

        full_page_text = "\n".join(l.text for l in assembled_lines)
        page_conf = sum(l.confidence for l in assembled_lines) / len(assembled_lines) if assembled_lines else 0.0
        dur_ms = round((time.perf_counter() - t0) * 1000.0, 2)

        return OCRPage(
            page_num=page_num,
            width=image.width,
            height=image.height,
            text=full_page_text,
            confidence=round(page_conf, 3),
            blocks=assembled_blocks,
            lines=assembled_lines,
            words=words,
            detected_languages=language_detector.detect_languages(full_page_text),
            processing_time_ms=dur_ms
        )
