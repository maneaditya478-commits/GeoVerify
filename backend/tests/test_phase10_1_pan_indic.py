"""Unit tests for Phase 10.1 Pan-Indic Multilingual Alignment & National Gazetteer."""

import pytest
from app.services.multilingual_alignment import multilingual_alignment_engine
from app.services.transliteration import transliteration_service
from app.verification.hierarchy import hierarchy_validator
from app.entity_resolution.candidates import MultiStageCandidateGenerator


def test_pan_indic_script_detection():
    # Tamil
    p, d, is_m = multilingual_alignment_engine.detect_scripts("மயிலாப்பூர், சென்னை, தமிழ்நாடு 600004")
    assert "Tamil" in d

    # Telugu
    p, d, is_m = multilingual_alignment_engine.detect_scripts("మాదాపూర్, హైదరాబాద్, తెలంగాణ 500081")
    assert "Telugu" in d

    # Kannada
    p, d, is_m = multilingual_alignment_engine.detect_scripts("ಇಂದಿರಾನಗರ, ಬೆಂಗಳೂರು, ಕರ್ನಾಟಕ ೫೬೦೦೩೮")
    assert "Kannada" in d

    # Bengali
    p, d, is_m = multilingual_alignment_engine.detect_scripts("শিবপুর, হাওড়া, পশ্চিমবঙ্গ ৭১১১০২")
    assert "Bengali" in d

    # Mixed
    p, d, is_m = multilingual_alignment_engine.detect_scripts("Hadapsar, हवेली, पुणे 411028")
    assert is_m is True


def test_pan_indic_administrative_abbreviation_expansion():
    # Tamil abbreviation
    res_ta = multilingual_alignment_engine.align_and_expand("கதவு 102, கிராஸ்கட் ரோடு, காந்திபுரம், மாவட்டம் கோயம்புத்தூர்")
    assert "District" in res_ta.expanded_address or len(res_ta.expanded_tokens) > 0

    # Telugu abbreviation
    res_te = multilingual_alignment_engine.align_and_expand("హనుమకొండ, మండలం హనుమకొండ, జిల్లా వరంగల్")
    assert "District" in res_te.expanded_address or len(res_te.expanded_tokens) > 0


def test_pan_indic_transliteration_mappings():
    # Tamil
    res_ta, _ = transliteration_service.transliterate_to_latin("சென்னை")
    assert "Chennai" in res_ta

    # Telugu
    res_te, _ = transliteration_service.transliterate_to_latin("హైదరాబాద్")
    assert "Hyderabad" in res_te

    # Kannada
    res_ka, _ = transliteration_service.transliterate_to_latin("ಬೆಂಗಳೂರು")
    assert "Bengaluru Urban" in res_ka

    # Bengali
    res_bn, _ = transliteration_service.transliterate_to_latin("কলকাতা")
    assert "Kolkata" in res_bn


def test_national_gazetteer_state_district_coverage():
    # Ensure all 36 States are loaded
    assert len(hierarchy_validator.states) == 36

    # Test district lookup in South, East, Northeast, North, West
    assert hierarchy_validator._match_district_entity("Chennai") is not None
    assert hierarchy_validator._match_district_entity("Howrah") is not None
    assert hierarchy_validator._match_district_entity("Kamrup Metropolitan") is not None
    assert hierarchy_validator._match_district_entity("Ludhiana") is not None
    assert hierarchy_validator._match_district_entity("Surat") is not None
