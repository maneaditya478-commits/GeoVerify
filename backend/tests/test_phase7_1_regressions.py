"""Regression and unit tests for Phase 7.1 Address Extraction Calibration & Provenance."""

import pytest
from app.document.models import (
    AddressRegion,
    ExtractedAddressField,
    ExtractedAddressCandidate,
    ExtractionMethod,
    BoundingBox,
)
from app.document.address.ocr_normalizer import OCRNormalizer
from app.document.address.field_extractor import AddressFieldExtractor
from app.document.address.pin_recovery import PINFirstRecoveryService
from app.services.address_parser import AddressParser
from app.services.transliteration import transliteration_service


def test_extraction_method_enum_values():
    assert ExtractionMethod.EXPLICIT.value == "EXPLICIT"
    assert ExtractionMethod.PIN_RECOVERY.value == "PIN_RECOVERY"
    assert ExtractionMethod.ADMIN_CONTEXT_RECOVERY.value == "ADMIN_CONTEXT_RECOVERY"
    assert ExtractionMethod.OCR_REPAIRED.value == "OCR_REPAIRED"


def test_ocr_normalizer_pin_repair_with_leading_confused_char():
    normalizer = OCRNormalizer()
    # 'S60066' -> '560066' (S -> 5)
    repaired_s = normalizer.repair_pincode_candidate("S60066")
    assert repaired_s == "560066"

    # '411O14' -> '411014' (O -> 0)
    repaired_o = normalizer.repair_pincode_candidate("411O14")
    assert repaired_o == "411014"

    # 'I10001' -> '110001' (I -> 1)
    repaired_i = normalizer.repair_pincode_candidate("I10001")
    assert repaired_i == "110001"


def test_ocr_normalizer_devanagari_digits():
    normalizer = OCRNormalizer()
    text = "पत्ता: पुणे ४११०१४"
    normalized = normalizer.normalize_text(text)
    assert "411014" in normalized


def test_field_extractor_assigns_extraction_method():
    extractor = AddressFieldExtractor()
    region = AddressRegion(
        region_id="r1",
        full_region_text="Flat 402, Ganga Carnation, Near EON IT Park, Kharadi, Pune, Maharashtra 411014",
        confidence=0.95,
    )
    fields = extractor.extract_fields(region)
    assert "pincode" in fields
    assert fields["pincode"].extraction_method == ExtractionMethod.EXPLICIT
    assert fields["pincode"].normalized_value == "411014"


def test_field_extractor_repaired_pin_provenance():
    extractor = AddressFieldExtractor()
    region = AddressRegion(
        region_id="r2",
        full_region_text="Palm Meadows, Whitefield, Bengaluru S60066",
        confidence=0.88,
    )
    fields = extractor.extract_fields(region)
    assert "pincode" in fields
    assert fields["pincode"].extraction_method == ExtractionMethod.OCR_REPAIRED
    assert fields["pincode"].normalized_value == "560066"


def test_pin_recovery_provenance():
    recovery_service = PINFirstRecoveryService()
    candidate = ExtractedAddressCandidate(
        candidate_id="c1",
        raw_address_text="Ganga Carnation, Kharadi, 411014",
        assembled_address="Ganga Carnation, Kharadi, 411014",
        fields={
            "pincode": ExtractedAddressField(
                field_name="pincode",
                raw_value="411014",
                normalized_value="411014",
                confidence=0.98,
                extraction_method=ExtractionMethod.EXPLICIT,
            )
        },
    )
    recovered = recovery_service.recover_candidate(candidate)
    assert recovered.pin_recovered is True
    assert "district" in recovered.fields
    assert recovered.fields["district"].extraction_method == ExtractionMethod.PIN_RECOVERY
    assert recovered.fields["district"].normalized_value == "Pune"
    assert "state" in recovered.fields
    assert recovered.fields["state"].extraction_method == ExtractionMethod.PIN_RECOVERY
    assert recovered.fields["state"].normalized_value == "Maharashtra"


def test_indic_prefixed_abbreviations_marathi():
    prefixed = transliteration_service.extract_indic_prefixed_fields("जि. पुणे, ता. हवेली, गाव: खराडी, पिन: ४११०१४")
    assert "district" in prefixed
    assert prefixed["district"] == "Pune"
    assert "subdistrict" in prefixed
    assert prefixed["subdistrict"] == "Haveli"


def test_multi_token_locality_parsing():
    parsed = AddressParser.parse("Sea Breeze Apt, Hill Road, Bandra West, Mumbai, Maharashtra 400050")
    assert parsed.locality == "Bandra West"
    assert parsed.district == "Mumbai Suburban" or parsed.district == "Mumbai"
    assert parsed.state == "Maharashtra"
    assert parsed.pincode == "400050"


def test_multi_token_locality_delhi():
    parsed = AddressParser.parse("Shop 4, Inner Circle, Connaught Place, New Delhi, Delhi 110001")
    assert parsed.locality == "Connaught Place"
    assert parsed.district == "New Delhi"
    assert parsed.state == "Delhi"
    assert parsed.pincode == "110001"
