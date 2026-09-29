"""Unit tests for OCR engine abstraction, language detection, and mock engine (Phase 7)."""

import pytest
from PIL import Image

from app.document.ocr import get_ocr_engine
from app.document.ocr.mock_engine import MockOCREngine
from app.document.ocr.language_detection import detect_language_scripts, LanguageDetector
from app.document.models import OCRQualityStatus


def test_language_detection_english():
    text = "Flat 402, Ganga Carnation, Near EON IT Park, Kharadi, Pune, Maharashtra 411014"
    langs = detect_language_scripts(text)
    assert "eng" in langs
    assert langs["eng"] > 0.7


def test_language_detection_marathi():
    text = "पत्ता: फ्लॅट ४०२, गंगा कार्नेशन, खराडी, पुणे, महाराष्ट्र ४११०१४"
    langs = detect_language_scripts(text)
    assert "mar" in langs or "hin" in langs
    assert sum(langs.values()) > 0.5


def test_mock_ocr_engine_processing():
    engine = MockOCREngine()
    assert engine.is_available() is True
    assert engine.name in ["mock", "mock_ocr"]
    assert engine.engine_name in ["mock", "mock_ocr"]

    img = Image.new("RGB", (600, 400), color="white")
    page = engine.process_page(img, page_num=1)

    assert page.page_num == 1
    assert len(page.blocks) >= 1
    assert len(page.lines) >= 1
    assert len(page.words) >= 1
    assert page.confidence > 0.8
    assert "Address" in page.text or "Pune" in page.text


def test_ocr_engine_factory():
    mock_eng = get_ocr_engine("mock")
    assert isinstance(mock_eng, MockOCREngine)

    auto_eng = get_ocr_engine("auto")
    assert auto_eng.is_available() is True
