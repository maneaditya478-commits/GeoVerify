"""Unit and integration tests for Phase 5: Multi-Stage Candidate Generation and Phonetic Matching."""

import pytest
from app.entity_resolution.candidates import candidate_generator, MultiStageCandidateGenerator
from app.entity_resolution.matcher import entity_matcher
from app.entity_resolution.resolver import address_entity_resolver
from app.entity_resolution.models import EntityType
from app.services.phonetic import phonetic_service, IndianPhoneticEncoder
from app.services.transliteration import transliteration_service
from app.schemas.address import Coordinates


def test_phonetic_encoder_transformations():
    # Test Indian place name phonetic simplifications
    assert phonetic_service.simplify_phonetic("Kharadi") == phonetic_service.simplify_phonetic("Kharadi")
    assert phonetic_service.simplify_phonetic("Puna") == phonetic_service.simplify_phonetic("Pune")
    assert phonetic_service.simplify_phonetic("Nasik") == phonetic_service.simplify_phonetic("Nashik")
    assert phonetic_service.simplify_phonetic("Maharastra") == phonetic_service.simplify_phonetic("Maharashtra")


def test_phonetic_similarity_scoring():
    # High phonetic similarity for common variations
    sim_pune = phonetic_service.compute_phonetic_similarity("Puna", "Pune")
    assert sim_pune >= 0.85

    sim_nashik = phonetic_service.compute_phonetic_similarity("Nasik", "Nashik")
    assert sim_nashik >= 0.85

    sim_khardi = phonetic_service.compute_phonetic_similarity("Khardi", "Kharadi")
    assert sim_khardi >= 0.80


def test_transliteration_multi_form_generation():
    forms = transliteration_service.generate_normalized_forms("खराडी")
    assert forms["canonical_form"] == "खराडी"
    assert "kharadi" in forms["transliterated_form"]
    assert forms["phonetic_form"] != ""


def test_candidate_generation_exact_channel():
    cands = candidate_generator.generate_candidates("Kharadi", expected_type=EntityType.LOCALITY, limit=5)
    assert len(cands) >= 1
    assert cands[0].name == "Kharadi"
    assert cands[0].similarity_score == 1.0


def test_candidate_generation_alias_channel():
    # Test historical city alias
    cands = candidate_generator.generate_candidates("Poona", expected_type=EntityType.DISTRICT, limit=5)
    assert len(cands) >= 1
    assert any("Pune" in c.name for c in cands)

    # Test Bombay alias
    cands_bombay = candidate_generator.generate_candidates("Bombay", expected_type=EntityType.DISTRICT, limit=5)
    assert len(cands_bombay) >= 1
    assert any("Mumbai" in c.name for c in cands_bombay)


def test_candidate_generation_phonetic_channel():
    # Puna -> Pune
    cands = candidate_generator.generate_candidates("Puna", expected_type=EntityType.DISTRICT, limit=5)
    assert len(cands) >= 1
    assert any("Pune" in c.name for c in cands)


def test_candidate_generation_admin_context_channel():
    # Searching within Maharashtra & Pune district
    cands = candidate_generator.generate_candidates(
        "",
        expected_type=EntityType.LOCALITY,
        context_state="Maharashtra",
        context_district="Pune",
        limit=10
    )
    assert len(cands) >= 1
    # Should retrieve Pune localities like Kharadi, Hinjewadi, Baner
    loc_names = [c.name for c in cands]
    assert any(n in loc_names for n in ["Kharadi", "Viman Nagar", "Baner", "Hinjewadi"])


def test_candidate_generation_pin_channel():
    # 411014 -> Kharadi / Viman Nagar
    cands = candidate_generator.generate_candidates(
        "",
        expected_type=EntityType.LOCALITY,
        context_pin="411014",
        limit=5
    )
    assert len(cands) >= 1
    assert any(c.pincode == "411014" for c in cands)


def test_entity_matcher_multi_factor_score():
    cands = candidate_generator.generate_candidates("Kharadi", expected_type=EntityType.LOCALITY, limit=1)
    assert len(cands) >= 1
    cand = cands[0]

    match_res = entity_matcher.match_candidate(
        candidate=cand,
        query_text="Kharadi",
        context_state="Maharashtra",
        context_district="Pune",
        context_pin="411014"
    )
    assert match_res.match_score >= 85.0
    assert match_res.match_confidence == "HIGH"
    assert match_res.breakdown.name_similarity == 40.0
    assert match_res.breakdown.admin_context == 25.0


def test_end_to_end_resolver_with_complex_typo_address():
    res = address_entity_resolver.resolve_address("WTC, Khardi, Puna, Maharastra 411014")
    assert res.resolved_entities["state"] is not None
    assert res.resolved_entities["state"].name == "Maharashtra"
    assert res.resolved_entities["district"] is not None
    assert res.resolved_entities["district"].name == "Pune"
    assert res.resolved_entities["locality"] is not None
    assert res.resolved_entities["locality"].name == "Kharadi"
    assert len(res.candidate_matches) >= 1
