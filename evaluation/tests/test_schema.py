"""Unit tests for evaluation dataset schema and models."""

import pytest
from evaluation.schema import (
    BenchmarkRecord,
    GroundTruth,
    BenchmarkMetadata,
    SourceType,
    BenchmarkCategory,
    Language,
    Script,
    ExpectedStatus,
    CompletenessLevel,
    BenchmarkDataset
)


def test_benchmark_record_schema_valid():
    """Verify valid BenchmarkRecord creation and validation."""
    gt = GroundTruth(
        country="India",
        state="Maharashtra",
        state_code="MH",
        district="Pune",
        subdistrict="Haveli",
        locality="Kharadi",
        pincode="411014"
    )
    rec = BenchmarkRecord(
        id="GV-000001",
        address="Kharadi, Pune, Maharashtra 411014",
        source_type=SourceType.SYNTHETIC,
        ground_truth=gt,
        category=BenchmarkCategory.COMPLETE_VALID,
        language=Language.EN,
        script=Script.LATIN,
        expected_status=ExpectedStatus.VERIFIED,
        metadata=BenchmarkMetadata(completeness=CompletenessLevel.COMPLETE, ambiguity=False)
    )
    assert rec.id == "GV-000001"
    assert rec.ground_truth.district == "Pune"
    assert rec.category == BenchmarkCategory.COMPLETE_VALID
    assert rec.source_type == SourceType.SYNTHETIC


def test_benchmark_record_incomplete_ground_truth():
    """Verify BenchmarkRecord allows incomplete ground truth fields."""
    gt = GroundTruth(state="Maharashtra")
    rec = BenchmarkRecord(
        id="GV-000002",
        address="Maharashtra",
        source_type=SourceType.SYNTHETIC,
        ground_truth=gt,
        category=BenchmarkCategory.INCOMPLETE,
        language=Language.EN,
        script=Script.LATIN,
        expected_status=ExpectedStatus.NEEDS_REVIEW,
        metadata=BenchmarkMetadata(completeness=CompletenessLevel.MINIMAL)
    )
    assert rec.ground_truth.district is None
    assert rec.ground_truth.locality is None
    assert rec.expected_status == ExpectedStatus.NEEDS_REVIEW


def test_benchmark_dataset_collection():
    """Verify BenchmarkDataset contains records and serializes properly."""
    gt = GroundTruth(state="Maharashtra", district="Pune")
    rec = BenchmarkRecord(
        id="GV-000003",
        address="Pune, Maharashtra",
        source_type=SourceType.SYNTHETIC,
        ground_truth=gt,
        category=BenchmarkCategory.PARTIAL_VALID,
        expected_status=ExpectedStatus.CONSISTENT
    )
    ds = BenchmarkDataset(
        version="1.0.0",
        generated_at="2026-09-29T12:00:00Z",
        total_cases=1,
        cases=[rec]
    )
    assert ds.total_cases == 1
    assert len(ds.cases) == 1
    d = ds.model_dump()
    assert d["cases"][0]["id"] == "GV-000003"
