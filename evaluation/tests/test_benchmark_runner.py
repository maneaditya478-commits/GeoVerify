"""Unit tests for BenchmarkRunner and DatasetLoader."""

import pytest
from pathlib import Path
from evaluation.generate_dataset import BenchmarkGenerator
from evaluation.schema import BenchmarkRecord, GroundTruth, BenchmarkCategory, ExpectedStatus
from evaluation.run_benchmark import BenchmarkRunner


def test_benchmark_generator_size_and_reproducibility():
    """Verify benchmark generator generates requested size and is deterministic with seed."""
    gen1 = BenchmarkGenerator(seed=42)
    ds1 = gen1.generate(target_size=50)

    gen2 = BenchmarkGenerator(seed=42)
    ds2 = gen2.generate(target_size=50)

    assert ds1.total_cases == ds2.total_cases
    assert len(ds1.cases) >= 50
    assert ds1.cases[0].address == ds2.cases[0].address
    assert ds1.cases[0].id == ds2.cases[0].id


@pytest.mark.asyncio
async def test_benchmark_runner_single_case():
    """Verify evaluate_case produces a valid EvaluationResultRecord."""
    rec = BenchmarkRecord(
        id="GV-TEST-001",
        address="World Trade Center, Kharadi, Haveli, Pune, Maharashtra 411014",
        ground_truth=GroundTruth(
            state="Maharashtra", district="Pune", subdistrict="Haveli", locality="Kharadi", pincode="411014"
        ),
        category=BenchmarkCategory.COMPLETE_VALID,
        expected_status=ExpectedStatus.VERIFIED
    )
    runner = BenchmarkRunner()
    result = await runner.evaluate_case(rec)
    assert result.case_id == "GV-TEST-001"
    assert result.state_matched is True
    assert result.district_matched is True
    assert result.locality_matched is True
    assert result.status_matched is True
    assert result.latency_ms > 0
