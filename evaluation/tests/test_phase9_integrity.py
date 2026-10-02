"""Integrity and Invariant tests for Phase 9 Architecture."""

import pytest
from app.config import settings
from app.temporal.resolver import temporal_resolver
from app.graph.graph_engine import geographic_graph
from app.evidence.probabilistic import probabilistic_evidence_model


def test_phase9_version_and_config_invariants():
    assert settings.APP_VERSION in ["9.0.0", "10.0.0"]
    assert settings.GEOVERIFY_CONFIG_VERSION in ["9.0.0", "10.0.0"]


def test_deterministic_failure_semantics_not_altered_by_ml():
    """Missing fields must yield UNKNOWN or MISSING, never manufactured certainty."""
    profile = probabilistic_evidence_model.calculate_confidence_profile(
        candidate_match_score=0.0,
        is_hierarchy_consistent=False,
        hierarchy_score_pct=0.0,
        is_ambiguous=False,
        top_candidate_margin=0.0,
        has_locality=False,
        has_district=False,
        has_state=False,
        has_pincode=False
    )
    assert profile.evidence_completeness == 0.0
    assert profile.candidate_confidence == 0.0
    assert profile.composite_confidence < 0.20


def test_temporal_graph_bidirectional_consistency():
    hist_nodes = [nid for nid in geographic_graph.find_nodes_by_name("Bombay") if nid.startswith("hist_")]
    curr_nodes = [nid for nid in geographic_graph.find_nodes_by_name("Mumbai") if not nid.startswith("hist_")]
    assert len(hist_nodes) >= 1
    assert len(curr_nodes) >= 1

    path = geographic_graph.find_path(hist_nodes[0], curr_nodes[0], max_depth=2)
    assert path is not None
    assert path.total_depth >= 1
