"""Unit tests for Phase 9 Probabilistic Evidence & Confidence Calibration."""

import pytest
from app.evidence.probabilistic import (
    ProbabilisticEvidenceModel,
    probabilistic_evidence_model,
    ConfidenceProfile,
    CalibrationReport,
)


def test_confidence_profile_high_quality():
    profile = probabilistic_evidence_model.calculate_confidence_profile(
        candidate_match_score=95.0,
        is_hierarchy_consistent=True,
        hierarchy_score_pct=100.0,
        is_ambiguous=False,
        top_candidate_margin=0.25,
        has_locality=True,
        has_district=True,
        has_state=True,
        has_pincode=True,
        has_landmark=True
    )
    assert profile.candidate_confidence >= 0.90
    assert profile.geographic_consistency_confidence >= 0.90
    assert profile.ambiguity_confidence >= 0.70
    assert profile.evidence_completeness >= 0.90
    assert profile.composite_confidence >= 0.85
    assert profile.is_calibrated is True


def test_confidence_profile_conflict_low_quality():
    profile = probabilistic_evidence_model.calculate_confidence_profile(
        candidate_match_score=40.0,
        is_hierarchy_consistent=False,
        hierarchy_score_pct=20.0,
        is_ambiguous=True,
        top_candidate_margin=0.02,
        has_locality=True,
        has_district=False,
        has_state=False,
        has_pincode=False
    )
    assert profile.geographic_consistency_confidence <= 0.35
    assert profile.composite_confidence <= 0.50


def test_brier_score_computation():
    # Perfect predictions
    preds = [1.0, 0.0, 1.0, 0.0]
    truth = [1, 0, 1, 0]
    brier = probabilistic_evidence_model.compute_brier_score(preds, truth)
    assert brier == 0.0

    # Intermediate predictions
    preds2 = [0.8, 0.2, 0.9, 0.1]
    truth2 = [1, 0, 1, 0]
    brier2 = probabilistic_evidence_model.compute_brier_score(preds2, truth2)
    assert brier2 < 0.05


def test_calibration_report():
    preds = [0.1, 0.2, 0.8, 0.9, 0.85, 0.15]
    truth = [0, 0, 1, 1, 1, 0]
    report = probabilistic_evidence_model.compute_calibration_report(preds, truth, n_bins=5)
    assert isinstance(report, CalibrationReport)
    assert report.total_samples == 6
    assert report.expected_calibration_error >= 0.0
    assert len(report.bins) == 5
