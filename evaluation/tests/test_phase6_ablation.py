"""Unit and Integration Tests for Phase 6 Ablation Study and Comparison CLIs."""

import pytest
from pathlib import Path
from evaluation.run_ablation import AblationStudyRunner
from evaluation.analyze_ranking_errors import Phase6ErrorAnalyzer
from evaluation.run_ambiguity_calibration import AmbiguityCalibrator
from evaluation.load_dataset import DatasetLoader


def test_ablation_runner_configs():
    """Verify all 8 ablation configurations are defined and valid."""
    runner = AblationStudyRunner()
    configs = runner._get_ablation_configs()

    assert len(configs) >= 8
    assert "Full_Phase6_Model" in configs
    assert "Ablation_No_Admin_Penalties" in configs
    assert "Phase5_Baseline" in configs

    # Verify Full Phase 6 has all penalties enabled
    p6 = configs["Full_Phase6_Model"]
    assert p6.penalties.state_conflict == -40.0
    assert p6.penalties.district_conflict == -25.0

    # Verify Ablation No Admin Penalties has 0 penalties
    no_pen = configs["Ablation_No_Admin_Penalties"]
    assert no_pen.penalties.state_conflict == 0.0


def test_ablation_runner_evaluation_subset():
    """Verify AblationStudyRunner executes correctly on a small dataset sample."""
    ds = DatasetLoader.load_default_dataset()
    cases = ds.cases[:5]

    runner = AblationStudyRunner()
    configs = runner._get_ablation_configs()

    p6_cfg = configs["Full_Phase6_Model"]
    res = runner.evaluate_config_on_cases("Full_Phase6_Model", p6_cfg, cases)

    assert "recall_at_1" in res
    assert "recall_at_5" in res
    assert 0.0 <= res["recall_at_1"] <= 1.0


def test_ambiguity_calibration_thresholds():
    """Verify AmbiguityCalibrator evaluates multiple delta thresholds."""
    calibrator = AmbiguityCalibrator()
    thresholds = [8.0, 12.0, 15.0]
    
    # Run evaluation on threshold list
    results = calibrator.evaluate_thresholds(thresholds=thresholds)

    assert len(results) == 3
    for r in results:
        assert "threshold_delta" in r
        assert "precision" in r
        assert "recall" in r
        assert "f1_score" in r
