"""Unit and Integration Tests for Phase 6 Context-Aware Candidate Ranking."""

import pytest
from app.entity_resolution.ranking import ContextAwareRanker, context_aware_ranker
from app.entity_resolution.ranking_config import (
    Phase6RankingConfig,
    RankingWeightsConfig,
    AdminPenaltiesConfig,
    ConfidenceBandsConfig
)
from app.entity_resolution.models import (
    CandidateEntity,
    EntityType,
    EntityMatchResult,
    RankingExplanation,
    AppliedPenalty
)
from app.schemas.address import Coordinates


def test_context_aware_ranker_multi_factor_scoring():
    """Verify all 9 scoring features contribute correctly to candidate score."""
    cand = CandidateEntity(
        id="loc_kharadi_pune",
        name="Kharadi",
        entity_type=EntityType.LOCALITY,
        state="Maharashtra",
        district="Pune",
        subdistrict="Haveli",
        pincode="411014",
        coordinates=Coordinates(latitude=18.5514, longitude=73.9405),
        bbox=[73.92, 18.53, 73.96, 18.57],
        similarity_score=1.0,
        match_source="exact",
        channels=["exact", "alias", "admin_context"]
    )

    ranker = ContextAwareRanker()
    res = ranker.score_candidate(
        candidate=cand,
        query_text="Kharadi",
        context_state="Maharashtra",
        context_district="Pune",
        context_subdistrict="Haveli",
        context_pin="411014",
        context_coordinates=Coordinates(latitude=18.5514, longitude=73.9405),
        expected_type=EntityType.LOCALITY
    )

    assert res.match_score >= 95.0
    assert res.match_confidence == "HIGH"
    assert res.breakdown.name_similarity == 25.0
    assert res.breakdown.admin_context == 25.0
    assert res.breakdown.parent_child_compatibility == 15.0
    assert res.breakdown.pin_compatibility == 10.0
    assert res.breakdown.geographic_proximity == 10.0
    assert res.breakdown.entity_type_weight == 5.0
    assert res.breakdown.retrieval_consensus == 3.0
    assert res.breakdown.data_quality == 2.0
    assert res.breakdown.penalty_deduction == 0.0


def test_state_conflict_penalty():
    """Verify -40.0 point deduction when candidate state contradicts asserted state."""
    cand = CandidateEntity(
        id="loc_kharadi_wrong_state",
        name="Kharadi",
        entity_type=EntityType.LOCALITY,
        state="Gujarat",  # Contradicts Maharashtra
        district="Ahmedabad",
        similarity_score=1.0,
        match_source="exact"
    )

    ranker = ContextAwareRanker()
    res = ranker.score_candidate(
        candidate=cand,
        query_text="Kharadi",
        context_state="Maharashtra",
        expected_type=EntityType.LOCALITY
    )

    assert any(p.name == "STATE_CONFLICT" for p in res.ranking_explanation.applied_penalties)
    assert res.ranking_explanation.total_penalty_deduction <= -40.0
    assert res.match_score < 50.0


def test_district_conflict_penalty():
    """Verify -25.0 point deduction when candidate district contradicts asserted district."""
    cand = CandidateEntity(
        id="loc_kharadi_nagpur",
        name="Kharadi",
        entity_type=EntityType.LOCALITY,
        state="Maharashtra",
        district="Nagpur",  # Contradicts Pune
        similarity_score=1.0,
        match_source="exact"
    )

    ranker = ContextAwareRanker()
    res = ranker.score_candidate(
        candidate=cand,
        query_text="Kharadi",
        context_state="Maharashtra",
        context_district="Pune",
        expected_type=EntityType.LOCALITY
    )

    assert any(p.name == "DISTRICT_CONFLICT" for p in res.ranking_explanation.applied_penalties)
    assert res.breakdown.penalty_deduction <= -25.0


def test_entity_type_mismatch_penalty():
    """Verify -30.0 point deduction when a District entity matches a Locality search."""
    district_cand = CandidateEntity(
        id="dist_pune",
        name="Pune",
        entity_type=EntityType.DISTRICT,
        state="Maharashtra",
        district="Pune",
        similarity_score=1.0,
        match_source="exact"
    )

    ranker = ContextAwareRanker()
    res = ranker.score_candidate(
        candidate=district_cand,
        query_text="Pune",
        context_state="Maharashtra",
        expected_type=EntityType.LOCALITY
    )

    assert any(p.name == "ENTITY_TYPE_MISMATCH" for p in res.ranking_explanation.applied_penalties)
    assert res.ranking_explanation.total_penalty_deduction <= -30.0


def test_pin_circle_conflict_penalty():
    """Verify -20.0 point deduction when candidate PIN has completely conflicting circle."""
    cand = CandidateEntity(
        id="loc_koramangala",
        name="Koramangala",
        entity_type=EntityType.LOCALITY,
        state="Karnataka",
        district="Bengaluru Urban",
        pincode="560034",
        similarity_score=1.0,
        match_source="exact"
    )

    ranker = ContextAwareRanker()
    res = ranker.score_candidate(
        candidate=cand,
        query_text="Koramangala",
        context_pin="110001",  # Delhi PIN contradicts 560xxx
        expected_type=EntityType.LOCALITY
    )

    assert any(p.name == "PIN_CIRCLE_CONFLICT" for p in res.ranking_explanation.applied_penalties)


def test_rank_candidates_sorting_and_explanations():
    """Verify candidates are sorted descending by score and enriched with delta explanations."""
    cand1 = CandidateEntity(
        id="cand_best",
        name="Kharadi",
        entity_type=EntityType.LOCALITY,
        state="Maharashtra",
        district="Pune",
        pincode="411014",
        similarity_score=1.0,
        match_source="exact",
        channels=["exact", "alias"]
    )
    cand2 = CandidateEntity(
        id="cand_diff_district",
        name="Kharadi",
        entity_type=EntityType.LOCALITY,
        state="Maharashtra",
        district="Thane",
        similarity_score=0.9,
        match_source="fuzzy"
    )

    ranker = ContextAwareRanker()
    ranked = ranker.rank_candidates(
        candidates=[cand2, cand1],
        query_text="Kharadi",
        context_state="Maharashtra",
        context_district="Pune",
        context_pin="411014",
        expected_type=EntityType.LOCALITY
    )

    assert len(ranked) == 2
    assert ranked[0].candidate.id == "cand_best"
    assert ranked[0].ranking_explanation.rank == 1
    assert ranked[0].ranking_explanation.score_delta_to_next is not None
    assert ranked[0].ranking_explanation.score_delta_to_next > 0
    assert ranked[1].candidate.id == "cand_diff_district"
    assert ranked[1].ranking_explanation.rank == 2


def test_confidence_bands_categorization():
    """Verify HIGH, MEDIUM, LOW confidence band categorization based on config thresholds."""
    config = Phase6RankingConfig(
        confidence=ConfidenceBandsConfig(
            high_threshold=85.0,
            medium_threshold=65.0,
            low_threshold=40.0
        )
    )
    ranker = ContextAwareRanker(config=config)

    # High match candidate
    c_high = CandidateEntity(
        id="c_high",
        name="Indiranagar",
        entity_type=EntityType.LOCALITY,
        state="Karnataka",
        district="Bengaluru Urban",
        similarity_score=1.0,
        match_source="exact"
    )
    res_high = ranker.score_candidate(c_high, "Indiranagar", context_state="Karnataka", context_district="Bengaluru Urban")
    assert res_high.match_confidence in ["HIGH", "MEDIUM"]

    # Low match candidate with conflict
    c_low = CandidateEntity(
        id="c_low",
        name="Indiranagar",
        entity_type=EntityType.DISTRICT,
        state="Tamil Nadu",
        district="Chennai",
        similarity_score=0.4,
        match_source="fuzzy"
    )
    res_low = ranker.score_candidate(c_low, "Indiranagar", context_state="Karnataka", expected_type=EntityType.LOCALITY)
    assert res_low.match_confidence == "LOW"


def test_subdistrict_conflict_penalty():
    """Verify -15.0 point deduction when candidate subdistrict contradicts asserted taluka."""
    cand = CandidateEntity(
        id="loc_hadapsar_pune",
        name="Hadapsar",
        entity_type=EntityType.LOCALITY,
        state="Maharashtra",
        district="Pune",
        subdistrict="Haveli",
        similarity_score=1.0,
        match_source="exact"
    )

    ranker = ContextAwareRanker()
    res = ranker.score_candidate(
        candidate=cand,
        query_text="Hadapsar",
        context_state="Maharashtra",
        context_district="Pune",
        context_subdistrict="Baramati",  # Contradicts Haveli
        expected_type=EntityType.LOCALITY
    )

    assert any(p.name == "SUBDISTRICT_CONFLICT" for p in res.ranking_explanation.applied_penalties)
    assert res.ranking_explanation.total_penalty_deduction <= -15.0


def test_retrieval_consensus_bonus():
    """Verify bonus points for candidates retrieved across 3 independent channels."""
    c_single = CandidateEntity(
        id="c_single",
        name="Kharadi",
        entity_type=EntityType.LOCALITY,
        similarity_score=0.9,
        match_source="fuzzy",
        channels=["fuzzy"]
    )
    c_multi = CandidateEntity(
        id="c_multi",
        name="Kharadi",
        entity_type=EntityType.LOCALITY,
        similarity_score=0.9,
        match_source="multi_channel",
        channels=["exact", "alias", "admin_context"]
    )

    ranker = ContextAwareRanker()
    res_single = ranker.score_candidate(c_single, "Kharadi")
    res_multi = ranker.score_candidate(c_multi, "Kharadi")

    assert res_multi.breakdown.retrieval_consensus > res_single.breakdown.retrieval_consensus
    assert res_multi.ranking_explanation.consensus_count == 3


def test_data_quality_scoring():
    """Verify full data quality points for candidates with complete coordinates and bounding box."""
    c_rich = CandidateEntity(
        id="c_rich",
        name="Koramangala",
        entity_type=EntityType.LOCALITY,
        coordinates=Coordinates(latitude=12.9352, longitude=77.6245),
        bbox=[77.61, 12.92, 77.64, 12.95],
        similarity_score=1.0,
        match_source="exact"
    )
    c_sparse = CandidateEntity(
        id="c_sparse",
        name="Koramangala",
        entity_type=EntityType.LOCALITY,
        similarity_score=1.0,
        match_source="exact"
    )

    ranker = ContextAwareRanker()
    res_rich = ranker.score_candidate(c_rich, "Koramangala")
    res_sparse = ranker.score_candidate(c_sparse, "Koramangala")

    assert res_rich.breakdown.data_quality > res_sparse.breakdown.data_quality
    assert res_rich.breakdown.data_quality == 2.0


def test_transliteration_phonetic_scoring():
    """Verify transliteration and Indic phonetic agreement features."""
    c_devanagari = CandidateEntity(
        id="c_dev",
        name="Kharadi",
        name_mr="खराडी",
        entity_type=EntityType.LOCALITY,
        similarity_score=1.0,
        match_source="transliteration"
    )

    ranker = ContextAwareRanker()
    res = ranker.score_candidate(c_devanagari, "खराडी")
    assert res.breakdown.transliteration_phonetic == 5.0

