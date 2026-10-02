"""Unit tests for Phase 10.1 Datasets and Evaluation Suite."""

import pytest
from pathlib import Path
from evaluation.phase10_1.dataset_generator import generate_phase10_1_partition, save_phase10_1_datasets
from evaluation.phase10_1.benchmark_runner import Phase10_1BenchmarkRunner


def test_phase10_1_dataset_generation_and_hashing(tmp_path):
    dev_file = tmp_path / "dev.json"
    val_file = tmp_path / "val.json"

    dev_hash, val_hash = save_phase10_1_datasets(str(dev_file), str(val_file))
    assert len(dev_hash) == 64
    assert len(val_hash) == 64
    assert dev_hash != val_hash


def test_phase10_1_splits_isolation():
    dev_data = generate_phase10_1_partition(100, "dev", base_seed=111)
    val_data = generate_phase10_1_partition(100, "val", base_seed=222)

    dev_ids = {c["case_id"] for c in dev_data["cases"]}
    val_ids = {c["case_id"] for c in val_data["cases"]}

    assert len(dev_ids.intersection(val_ids)) == 0
    assert all(c["case_id"].startswith("P10_1_DEV_") for c in dev_data["cases"])
    assert all(c["case_id"].startswith("P10_1_VAL_") for c in val_data["cases"])


@pytest.mark.asyncio
async def test_phase10_1_runner_sample():
    runner = Phase10_1BenchmarkRunner()
    sample_cases = [
        {
            "case_id": "TEST_001",
            "raw_address": "Flat 402, Magarpatta City, Hadapsar, Pune, Maharashtra 411028",
            "expected_locality_canonical": "Hadapsar",
            "expected_district_canonical": "Pune",
            "locality": "Hadapsar",
            "district": "Pune",
            "state": "Maharashtra",
            "pincode": "411028",
            "settlement_type": "Urban",
            "region": "West",
            "expected_status": "VERIFIED",
            "ocr_level": 0
        }
    ]
    results = await runner.evaluate_dataset(sample_cases)
    assert results["overall_metrics"]["total_cases"] == 1
    assert results["overall_metrics"]["status_accuracy"] == 100.0
    assert results["overall_metrics"]["recall_at_5"] == 100.0
