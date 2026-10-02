"""Unit tests for Phase 9 Calibration Evaluator."""

import pytest
from evaluation.phase9.dataset_generator import generate_phase9_dataset
from evaluation.phase9.calibration_evaluator import CalibrationEvaluator


def test_calibration_evaluator_metrics():
    manifest = generate_phase9_dataset(total_cases=100)
    comparison = CalibrationEvaluator.evaluate_calibration(manifest["heldout"])

    assert comparison.calibrated_report.brier_score <= comparison.uncalibrated_report.brier_score
    assert comparison.calibrated_report.expected_calibration_error <= 0.15
    assert len(comparison.calibrated_report.bins) == 10
    assert len(comparison.reliability_bins_calibrated) == 10
