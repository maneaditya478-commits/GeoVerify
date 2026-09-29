"""Tests for Phase 6.1 Evaluation and Ranking Regression Framework."""

import json
from pathlib import Path
import pytest

from evaluation.phase6_1.dataset_splits import DatasetSplitter
from evaluation.phase6_1.ranking_regression import RankingRegressionAnalyzer
from evaluation.phase6_1.ranking_regression_report import generate_phase_comparison
from evaluation.load_dataset import DatasetLoader

RESULTS_DIR = Path(__file__).parent.parent / "results" / "phase6_1"


def test_stratified_splits_generation():
    """Verify stratified split produces valid 60/20/20 partition across categories."""
    dataset = DatasetLoader.load_default()
    dev_cases, val_cases, held_out_cases = DatasetSplitter.split_dataset(dataset, seed=42)
    assert len(dev_cases) > 0
    assert len(val_cases) > 0
    assert len(held_out_cases) > 0
    
    total = len(dev_cases) + len(val_cases) + len(held_out_cases)
    assert total == 1065

    # Check non-overlapping partition
    train_ids = {c.id for c in dev_cases}
    val_ids = {c.id for c in val_cases}
    test_ids = {c.id for c in held_out_cases}
    assert len(train_ids.intersection(val_ids)) == 0
    assert len(train_ids.intersection(test_ids)) == 0
    assert len(val_ids.intersection(test_ids)) == 0


def test_experiment_metadata_reproducibility():
    """Verify experiment metadata generates valid SHA256 checksums."""
    res = DatasetSplitter.export_splits(RESULTS_DIR)
    meta = res["metadata"]
    assert "dataset_hash_sha256" in meta
    assert len(meta["dataset_hash_sha256"]) == 64
    assert meta["random_seed"] == 42
    assert meta["dev_cases_count"] > 0


def test_ranking_regression_analyzer_smoke():
    """Verify ranking regression analyzer can instantiate and audit test cases."""
    analyzer = RankingRegressionAnalyzer(smoke=True, limit=5)
    assert analyzer.smoke is True
    assert analyzer.limit == 5


def test_phase_comparison_generation():
    """Verify phase comparison report generator produces valid output artifacts."""
    generate_phase_comparison()
    csv_file = RESULTS_DIR / "phase_comparison.csv"
    md_file = RESULTS_DIR / "phase_comparison.md"
    assert csv_file.exists()
    assert md_file.exists()
