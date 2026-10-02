"""Unit tests for Phase 9 Benchmark Suite & Dataset Generator."""

import pytest
from evaluation.phase9.dataset_generator import generate_phase9_dataset
from evaluation.phase9.benchmark_runner import Phase9BenchmarkRunner


def test_dataset_generator_structure_and_splits():
    manifest = generate_phase9_dataset(total_cases=100)
    assert manifest["metadata"]["total_cases"] == 100
    assert len(manifest["dev"]) == 60
    assert len(manifest["val"]) == 20
    assert len(manifest["heldout"]) == 20

    categories = manifest["metadata"]["categories"]
    assert "temporal_historical" in categories
    assert "mixed_script_indic" in categories
    assert "landmark_anchored" in categories


@pytest.mark.asyncio
async def test_benchmark_runner_execution():
    manifest = generate_phase9_dataset(total_cases=10)
    runner = Phase9BenchmarkRunner()
    metrics = await runner.run_benchmark(manifest["val"])

    assert metrics.total_cases == 2
    assert metrics.recall_at_1 >= 0.0
    assert metrics.recall_at_5 >= metrics.recall_at_1
    assert metrics.mean_latency_ms > 0.0
