"""Unit & Regression Tests for GeoVerify India Phase 6.1.

Validates:
1. Ranking penalty calibration (subdistrict conflict does not overpenalize when state & district match).
2. Low name similarity penalty preventing non-lexical candidate takeover.
3. Entity type mismatch enforcement when resolving localities.
4. O(1) indexed hierarchy validation for states, districts, and aliases.
5. In-memory candidate generation speed and correctness.
"""

import json
import pytest
from pathlib import Path

from app.entity_resolution.models import CandidateEntity, EntityType
from app.entity_resolution.ranking import ContextAwareCandidateRanker
from app.entity_resolution.candidates import candidate_generator
from app.verification.hierarchy import hierarchy_validator
from app.verification.decision_engine import decision_engine
from app.verification.engine import verification_engine

FIXTURES_PATH = Path(__file__).parent / "fixtures" / "phase6_1_regressions.json"


@pytest.fixture
def ranker():
    return ContextAwareCandidateRanker()


def test_fixtures_file_exists():
    assert FIXTURES_PATH.exists()
    with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) >= 5


def test_subdistrict_conflict_not_overpenalized(ranker):
    """When state and district are exact matches, subdistrict mismatch should not apply punitive penalty."""
    cand = CandidateEntity(
        id="loc_bandra_west",
        name="Bandra West",
        entity_type=EntityType.LOCALITY,
        state="Maharashtra",
        district="Mumbai Suburban",
        subdistrict="Bandra",
        pincode="400050",
        similarity_score=1.0,
        match_source="exact"
    )
    # Query asserts wrong subdistrict "Mulshi", but correct state & district
    res = ranker.score_candidate(
        candidate=cand,
        query_text="Bandra West",
        context_state="Maharashtra",
        context_district="Mumbai Suburban",
        context_subdistrict="Mulshi",
        expected_type=EntityType.LOCALITY
    )
    penalty_names = [p.name for p in res.ranking_explanation.applied_penalties]
    assert "SUBDISTRICT_CONFLICT" in penalty_names
    assert res.match_score >= 60.0


def test_low_name_similarity_penalty(ranker):
    """A candidate with negligible lexical similarity to query token receives low name penalty."""
    unrelated_cand = CandidateEntity(
        id="loc_powai",
        name="Powai",
        entity_type=EntityType.LOCALITY,
        state="Maharashtra",
        district="Mumbai Suburban",
        pincode="400076",
        similarity_score=0.1,
        match_source="admin_context"
    )
    res = ranker.score_candidate(
        candidate=unrelated_cand,
        query_text="Kharadi",
        context_state="Maharashtra",
        context_district="Mumbai Suburban",
        expected_type=EntityType.LOCALITY
    )
    penalty_names = [p.name for p in res.ranking_explanation.applied_penalties]
    assert "LOW_NAME_SIMILARITY" in penalty_names
    assert res.match_score < 50.0


def test_entity_type_mismatch_penalty(ranker):
    """A non-locality entity (e.g. PIN or District) receives ENTITY_TYPE_MISMATCH when expected is LOCALITY."""
    pin_cand = CandidateEntity(
        id="pin_400050",
        name="400050",
        entity_type=EntityType.PINCODE,
        state="Maharashtra",
        district="Mumbai Suburban",
        pincode="400050",
        similarity_score=1.0,
        match_source="pin"
    )
    res = ranker.score_candidate(
        candidate=pin_cand,
        query_text="Bandra West",
        context_state="Maharashtra",
        context_district="Mumbai Suburban",
        expected_type=EntityType.LOCALITY
    )
    penalty_names = [p.name for p in res.ranking_explanation.applied_penalties]
    assert "ENTITY_TYPE_MISMATCH" in penalty_names


def test_fast_hierarchy_indexing():
    """Verify O(1) indexed hierarchy validation works for canonical and alias names."""
    # Canonical state + district
    res1 = hierarchy_validator.validate_hierarchy(state="Maharashtra", district="Pune")
    assert res1.is_consistent is True
    assert res1.state == "Maharashtra"
    assert res1.district == "Pune"

    # Alias district (Bangalore -> Bengaluru Urban)
    res2 = hierarchy_validator.validate_hierarchy(state="Karnataka", district="Bangalore")
    assert res2.is_consistent is True
    assert res2.district == "Bengaluru Urban"

    # Invalid cross-state hierarchy
    res3 = hierarchy_validator.validate_hierarchy(state="Maharashtra", district="Bengaluru Urban")
    assert res3.is_consistent is False


def test_candidate_generator_indices():
    """Verify candidate generator builds lookups and retrieves exact matches in O(1)."""
    cands = candidate_generator.generate_candidates(token="Kharadi", expected_type=EntityType.LOCALITY, limit=5)
    assert len(cands) > 0
    assert any(c.name == "Kharadi" for c in cands)


@pytest.mark.asyncio
async def test_pipeline_end_to_end_consistency():
    """Verify end-to-end verification produces verified status for a complete valid address."""
    from app.schemas.address import VerificationRequest
    req = VerificationRequest(address="Kharadi, Pune, Maharashtra 411014")
    result = await verification_engine.verify(req)
    assert result.status is not None
    assert result.status.value in ["VERIFIED", "PARTIALLY_VERIFIED", "CONSISTENT"]
    assert result.score >= 70


def test_pincode_prefix_indexing():
    """Verify PIN code prefix table is populated and operational."""
    assert len(candidate_generator.pincodes_by_prefix) > 0
    assert "41" in candidate_generator.pincodes_by_prefix
    p_list = candidate_generator.pincodes_by_prefix["41"]
    assert len(p_list) > 0
    assert any(str(p["pincode"]).startswith("41") for p in p_list)


def test_devanagari_transliteration_retrieval():
    """Verify Devanagari Hindi place names are retrieved with high similarity."""
    cands = candidate_generator.generate_candidates(token="खराडी", expected_type=EntityType.LOCALITY, limit=5)
    assert len(cands) > 0
    assert any(c.name == "Kharadi" for c in cands)


def test_decision_engine_calibration_consistent():
    """Verify decision engine evaluates clean consistent address into VERIFIED/CONSISTENT status."""
    from app.schemas.verification import PinVerificationResult, BoundaryVerificationResult
    from app.schemas.hierarchy import AdministrativeHierarchyResult
    
    h_res = AdministrativeHierarchyResult(
        is_consistent=True,
        state="Maharashtra",
        district="Pune"
    )
    p_res = PinVerificationResult(pincode="411014", is_valid_format=True, matched=True, matched_state="Maharashtra", matched_district="Pune")
    b_res = BoundaryVerificationResult(point_inside_state=True, point_inside_district=True)
    
    dec = decision_engine.evaluate(
        consistency_score=92,
        hierarchy=h_res,
        boundary=b_res,
        pin=p_res,
        is_ambiguous=False
    )
    assert dec.status.value in ["VERIFIED", "CONSISTENT"]
    assert dec.confidence_level in ["HIGH", "MEDIUM"]


def test_decision_engine_calibration_inconsistent():
    """Verify decision engine marks severe hierarchy conflict as INCONSISTENT."""
    from app.schemas.verification import PinVerificationResult, BoundaryVerificationResult
    from app.schemas.hierarchy import AdministrativeHierarchyResult
    
    h_res = AdministrativeHierarchyResult(
        is_consistent=False,
        state="Maharashtra",
        district="Bengaluru Urban",
        mismatch_details=["District Bengaluru Urban is not in Maharashtra"]
    )
    p_res = PinVerificationResult(pincode="411014", is_valid_format=True, matched=False)
    b_res = BoundaryVerificationResult(point_inside_state=False, point_inside_district=False)
    
    dec = decision_engine.evaluate(
        consistency_score=32,
        hierarchy=h_res,
        boundary=b_res,
        pin=p_res,
        is_ambiguous=False
    )
    assert dec.status.value in ["INCONSISTENT", "UNABLE_TO_VERIFY"]
