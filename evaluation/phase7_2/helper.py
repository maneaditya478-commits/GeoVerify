"""Helper utilities for Phase 7.2 evaluation suite."""

import io
from PIL import Image, ImageDraw
from evaluation.phase7_2.dataset import OCRTestCase


def generate_synthetic_document_image(test_case: OCRTestCase) -> bytes:
    """Renders text onto a synthetic image canvas with optional degradations."""
    img = Image.new("RGB", (900, 700), color=(250, 250, 250))
    draw = ImageDraw.Draw(img)

    # Draw simple header border
    draw.rectangle([(20, 20), (880, 680)], outline=(180, 180, 180), width=2)

    # Draw text lines
    lines = test_case.document_text.splitlines()
    y = 50
    for line in lines:
        draw.text((50, y), line, fill=(30, 30, 30))
        y += 35

    if test_case.degradation_type == "skew" and test_case.skew_angle:
        img = img.rotate(test_case.skew_angle, expand=False, fillcolor=(250, 250, 250))
    elif test_case.degradation_type == "low_contrast":
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(0.4)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
