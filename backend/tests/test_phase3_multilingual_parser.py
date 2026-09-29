"""Phase 3 tests for Multilingual Devanagari parsing, Indic prefixes, and mixed-language addresses."""

import pytest
from app.services.transliteration import transliteration_service
from app.services.address_parser import AddressParser
from app.services.normalizer import AddressNormalizer


def test_script_detection():
    """Verify script detection across Latin, Devanagari, and Mixed text."""
    assert transliteration_service.detect_script("Kharadi Pune") == "Latin"
    assert transliteration_service.detect_script("पुणे महाराष्ट्र") == "Devanagari"
    assert transliteration_service.detect_script("Kharadi, पुणे, Maharashtra") == "Mixed"


def test_transliteration_to_latin():
    """Verify transliteration of Devanagari terms to English canonicals."""
    text_mr = "खराडी, हवेली, पुणे, महाराष्ट्र"
    trans_lat, steps = transliteration_service.transliterate_to_latin(text_mr)
    assert "Kharadi" in trans_lat
    assert "Haveli" in trans_lat
    assert "Pune" in trans_lat
    assert "Maharashtra" in trans_lat
    assert len(steps) >= 4


def test_indic_prefix_extraction():
    """Verify extraction of formal prefix-labeled addresses."""
    labeled_text = "गाव: खराडी, तालुका: हवेली, जिल्हा: पुणे, राज्य: महाराष्ट्र, पिन: 411014"
    prefixed = transliteration_service.extract_indic_prefixed_fields(labeled_text)
    assert prefixed.get("locality") == "Kharadi"
    assert prefixed.get("subdistrict") == "Haveli"
    assert prefixed.get("district") == "Pune"
    assert prefixed.get("state") == "Maharashtra"
    assert prefixed.get("pincode") == "411014"


def test_parser_with_indic_prefixes():
    """Verify AddressParser automatically parses Indic prefix-labeled address."""
    labeled_text = "गाव: खराडी, तालुका: हवेली, जिल्हा: पुणे, राज्य: महाराष्ट्र, पिन: 411014"
    parsed = AddressParser.parse(labeled_text)
    assert parsed.locality == "Kharadi"
    assert parsed.subdistrict == "Haveli"
    assert parsed.district == "Pune"
    assert parsed.state == "Maharashtra"
    assert parsed.pincode == "411014"
    assert parsed.parse_confidence == 1.0


def test_parser_mixed_language_and_typos():
    """Verify mixed language parsing: English locality + Devanagari district + Latin state."""
    raw = "Kharadi, पुणे, Maharashtra 411014"
    parsed = AddressParser.parse(raw)
    assert parsed.locality == "Kharadi"
    assert parsed.district == "Pune"
    assert parsed.state == "Maharashtra"
    assert parsed.pincode == "411014"
    assert parsed.detected_script == "Mixed"


def test_hindi_delhi_address_parsing():
    """Verify parsing of Devanagari Delhi address with Connaught Place."""
    raw = "कनॉट प्लेस, नई दिल्ली 110001"
    parsed = AddressParser.parse(raw)
    assert parsed.locality == "Connaught Place"
    assert parsed.district == "New Delhi"
    assert parsed.state == "Delhi"
    assert parsed.pincode == "110001"
    assert parsed.detected_script == "Devanagari"


def test_devanagari_prefix_variations():
    """Verify prefix extraction with Gram / Tehsil / Zilla variations."""
    raw = "ग्राम: बाणेर, तहसील: हवेली, जिला: पुणे"
    prefixed = transliteration_service.extract_indic_prefixed_fields(raw)
    assert prefixed.get("locality") == "Baner"
    assert prefixed.get("subdistrict") == "Haveli"
    assert prefixed.get("district") == "Pune"

