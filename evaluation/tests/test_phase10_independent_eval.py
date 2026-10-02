"""Unit tests for Phase 10 Independent Dataset and Benchmark Runner."""

import json
import pytest
from pathlib import Path
from evaluation.phase10.independent_dataset_generator import generate_independent_phase10_benchmark, save_frozen_independent_dataset
from evaluation.phase10.independent_benchmark_runner import Phase10IndependentRunner, DatasetIntegrityError


def test_independent_dataset_generation_and_hashing(tmp_path):
    manifest = generate_independent_phase10_benchmark(total_target=50)
    assert manifest["metadata"]["total_cases"] == 50
    assert len(manifest["cases"]) == 50
    assert len(manifest["metadata"]["sha256"]) == 64

    # Save to temp file
    temp_file = tmp_path / "test_dataset.json"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f)

    # Verify integrity passes
    loaded = Phase10IndependentRunner.verify_dataset_integrity(str(temp_file))
    assert loaded["metadata"]["sha256"] == manifest["metadata"]["sha256"]


def test_dataset_integrity_failure_on_tampering(tmp_path):
    manifest = generate_independent_phase10_benchmark(total_target=20)
    temp_file = tmp_path / "tampered_dataset.json"

    # Tamper with one case
    manifest["cases"][0]["raw_address"] = "TAMPERED_ADDRESS"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f)

    # Expect DatasetIntegrityError
    with pytest.raises(DatasetIntegrityError):
        Phase10IndependentRunner.verify_dataset_integrity(str(temp_file))


@pytest.mark.asyncio
async def test_independent_runner_execution_sample():
    manifest = generate_independent_phase10_benchmark(total_target=10)
    runner = Phase10IndependentRunner()
    result = await runner.run_evaluation(manifest["cases"])

    metrics = result["overall_metrics"]
    assert metrics["total_cases"] == 10
    assert metrics["recall_at_1"] >= 0.0
    assert metrics["status_accuracy"] >= 0.0
    assert "regional_breakdown" in result
    assert "calibration" in result
