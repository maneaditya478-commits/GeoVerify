"""Unit tests for image preprocessing, deskewing, and quality evaluation (Phase 7)."""

import pytest
import numpy as np
from PIL import Image, ImageDraw

from app.document.image_preprocessor import ImagePreprocessor
from app.document.quality import DocumentQualityEvaluator, OCRQualityStatus


@pytest.fixture
def preprocessor():
    return ImagePreprocessor()


@pytest.fixture
def quality_evaluator():
    return DocumentQualityEvaluator()


def test_preprocessor_grayscale_and_rescale(preprocessor):
    img = Image.new("RGB", (400, 300), color="blue")
    processed, angle = preprocessor.preprocess(img)
    
    assert processed.mode == "L"  # Grayscale
    assert processed.width >= 400
    assert processed.height >= 300
    assert isinstance(angle, float)


def test_preprocessor_deskew_rotated_image(preprocessor):
    # Create image with horizontal text-like black lines
    img = Image.new("L", (500, 300), color=255)
    draw = ImageDraw.Draw(img)
    for y in range(50, 250, 20):
        draw.line([(50, y), (450, y)], fill=0, width=4)
    
    # Rotate by 5 degrees
    rotated = img.rotate(5, expand=True, fillcolor=255)
    processed, angle = preprocessor.preprocess(rotated)
    
    assert isinstance(angle, float)
    assert abs(angle) <= 15.0


def test_quality_evaluator_metrics(quality_evaluator):
    # High contrast, sharp synthetic test card
    img = Image.new("RGB", (600, 400), color="white")
    draw = ImageDraw.Draw(img)
    for y in range(30, 350, 30):
        draw.text((40, y), "Address: Flat 402, Ganga Carnation, Pune 411014", fill="black")

    report = quality_evaluator.evaluate(img)
    assert report.width == 600
    assert report.height == 400
    assert report.contrast_score >= 0.2
    assert report.quality_status in [OCRQualityStatus.HIGH, OCRQualityStatus.MEDIUM]


def test_quality_evaluator_blurry_image(quality_evaluator):
    # Uniform grey blurry image
    img = Image.new("L", (200, 200), color=128)
    report = quality_evaluator.evaluate(img)
    assert report.is_blurry is True
    assert report.is_low_contrast is True
    assert report.quality_status == OCRQualityStatus.LOW
