"""Unit tests for Phase 8 Adaptive Preprocessing and Multilingual Post-Correction."""

import io
import pytest
from PIL import Image

from app.document.preprocessing.adaptive import AdaptiveImagePreprocessor, ImageQualityProfile
from app.document.address.post_corrector import GeographicallyGroundedPostCorrector


def _create_test_image(width: int = 400, height: int = 300, color: tuple = (200, 200, 200)) -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class TestAdaptivePreprocessing:
    """Validates document quality analysis and adaptive image preprocessing."""

    def test_analyze_quality_low_resolution(self):
        img_bytes = _create_test_image(width=400, height=300)
        profile = AdaptiveImagePreprocessor.analyze_quality(img_bytes)

        assert isinstance(profile, ImageQualityProfile)
        assert profile.is_low_dpi is True
        assert "UPSCALE" in profile.recommended_operations

    def test_preprocess_upscales_low_dpi(self):
        img_bytes = _create_test_image(width=400, height=300)
        processed_bytes, applied_ops = AdaptiveImagePreprocessor.preprocess_image(img_bytes)

        assert any("UPSCALE" in op for op in applied_ops)
        out_img = Image.open(io.BytesIO(processed_bytes))
        assert out_img.width > 400

    def test_preprocess_force_deskew(self):
        img_bytes = _create_test_image(width=1000, height=1000)
        processed_bytes, applied_ops = AdaptiveImagePreprocessor.preprocess_image(
            img_bytes, force_deskew_angle=10.0
        )
        assert any("DESKEW" in op for op in applied_ops)


class TestMultilingualPostCorrector:
    """Validates geographically grounded post-corrector."""

    def setup_method(self):
        self.corrector = GeographicallyGroundedPostCorrector()

    def test_devanagari_numeral_translation(self):
        text = "पुणे ४११०३८"
        corrected, records = self.corrector.post_correct(text)
        assert "411038" in corrected
        assert any(r["type"] == "DEVANAGARI_NUMERALS" for r in records)

    def test_devanagari_geo_mapping(self):
        text = "कोथरूड पुणे महाराष्ट्र"
        corrected, records = self.corrector.post_correct(text)
        assert "Kothrud" in corrected
        assert "Pune" in corrected
        assert "Maharashtra" in corrected
        assert any(r["type"] == "DEVANAGARI_GEO_TRANSLITERATION" for r in records)

    def test_common_geo_typo_repair(self):
        text = "Flat 101, Indiranagr, Bengalooru, Karnatka"
        corrected, records = self.corrector.post_correct(text)
        assert "Indiranagar" in corrected
        assert "Bengaluru" in corrected
        assert "Karnataka" in corrected

    def test_grounded_state_repair_with_context(self):
        text = "Flat 12, Kothrud, Pune, Maharash"
        corrected, records = self.corrector.post_correct(text, context_state="Maharashtra")
        assert "Maharashtra" in corrected
