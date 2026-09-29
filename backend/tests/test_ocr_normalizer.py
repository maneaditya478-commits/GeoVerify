"""Unit tests for OCR text normalizer and PIN repair (Phase 7)."""

import pytest
from app.document.address.ocr_normalizer import OCRNormalizer


@pytest.fixture
def normalizer():
    return OCRNormalizer()


def test_devanagari_digit_normalization(normalizer):
    devanagari_text = "पिन: ४११०१४, फोन: ९८७६५४३२१०"
    normalized = normalizer.normalize_text(devanagari_text)
    assert "411014" in normalized
    assert "9876543210" in normalized


def test_admin_keyword_ocr_error_correction(normalizer):
    corrupted = "Ta1uka Haveli, D1st Pune, Maharashtr@"
    normalized = normalizer.normalize_text(corrupted)
    assert "Taluka Haveli" in normalized
    assert "District Pune" in normalized
    assert "Maharashtra" in normalized


def test_pincode_letter_substitution_repair(normalizer):
    # 'O' substituted for '0', 'l' for '1', 'S' for '5'
    test_cases = [
        ("PIN: 411O14", "411014"),
        ("PINCODE 56OOO1", "560001"),
        ("PIN: 4110l4", "411014"),
        ("PIN-11000S", "110005"),
    ]
    for raw_input, expected_pin in test_cases:
        res = normalizer.normalize_text(raw_input)
        assert expected_pin in res


def test_repair_pincode_candidate_direct(normalizer):
    assert normalizer.repair_pincode_candidate("411O14") == "411014"
    assert normalizer.repair_pincode_candidate("560OO1") == "560001"
    assert normalizer.repair_pincode_candidate("411014") == "411014"
    assert normalizer.repair_pincode_candidate("011014") is None  # Indian PIN cannot start with 0
    assert normalizer.repair_pincode_candidate("ABCDEF") is None
