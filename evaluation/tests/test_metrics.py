"""Unit tests for BenchmarkMetricsCalculator."""

import pytest
from evaluation.schema import EvaluationResultRecord
from evaluation.metrics import BenchmarkMetricsCalculator


def test_compute_accuracy_precision_recall_f1():
    """Verify precision, recall, and F1 calculations."""
    m = BenchmarkMetricsCalculator.compute_accuracy_precision_recall_f1(tp=80, fp=20, fn=10, tn=90)
    assert m["accuracy"] == 0.85
    assert m["precision"] == 0.80
    assert round(m["recall"], 4) == 0.8889
    assert round(m["f1"], 4) == 0.8421


def test_evaluate_all_records():
    """Verify full metrics evaluation across sample result records."""
    records = [
        EvaluationResultRecord(
            case_id="GV-001",
            address="Kharadi, Pune, Maharashtra 411014",
            category="COMPLETE_VALID",
            language="en",
            script="latin",
            source_type="SYNTHETIC",
            expected_state="Maharashtra",
            predicted_state="Maharashtra",
            state_matched=True,
            expected_district="Pune",
            predicted_district="Pune",
            district_matched=True,
            expected_subdistrict="Haveli",
            predicted_subdistrict="Haveli",
            subdistrict_matched=True,
            expected_locality="Kharadi",
            predicted_locality="Kharadi",
            locality_matched=True,
            expected_pincode="411014",
            predicted_pincode="411014",
            pincode_matched=True,
            exact_hierarchy_matched=True,
            expected_status="VERIFIED",
            predicted_status="VERIFIED",
            status_matched=True,
            expected_ambiguity=False,
            predicted_ambiguity=False,
            ambiguity_matched=True,
            candidate_recall_1=True,
            candidate_recall_3=True,
            candidate_recall_5=True,
            candidate_recall_10=True,
            consistency_score=94,
            completeness_score=90,
            entity_match_score=95.0,
            latency_ms=12.5
        ),
        EvaluationResultRecord(
            case_id="GV-002",
            address="Bilaspur",
            category="AMBIGUOUS_LOCALITY",
            language="en",
            script="latin",
            source_type="SYNTHETIC",
            expected_locality="Bilaspur",
            predicted_locality="Bilaspur",
            locality_matched=True,
            exact_hierarchy_matched=False,
            expected_status="AMBIGUOUS",
            predicted_status="AMBIGUOUS",
            status_matched=True,
            expected_ambiguity=True,
            predicted_ambiguity=True,
            ambiguity_matched=True,
            candidate_recall_1=True,
            candidate_recall_3=True,
            candidate_recall_5=True,
            candidate_recall_10=True,
            consistency_score=45,
            completeness_score=20,
            entity_match_score=85.0,
            latency_ms=8.0
        )
    ]

    metrics = BenchmarkMetricsCalculator.evaluate_all(records)
    assert metrics["total_cases"] == 2
    assert metrics["entity_resolution"]["state_accuracy"] == 1.0
    assert metrics["entity_resolution"]["district_accuracy"] == 1.0
    assert metrics["entity_resolution"]["exact_hierarchy_accuracy"] == 0.5
    assert metrics["candidate_recall"]["recall_at_1"] == 1.0
    assert metrics["status_classification"]["overall_accuracy"] == 1.0
    assert metrics["ambiguity"]["f1"] == 1.0
    assert metrics["latency"]["mean_ms"] > 0


def test_metrics_empty_records():
    """Verify metrics calculation on empty records list."""
    m = BenchmarkMetricsCalculator.evaluate_all([])
    assert m["total_cases"] == 0


def test_metrics_confusion_matrix_shape():
    """Verify confusion matrix contains all 6 status classes."""
    records = [
        EvaluationResultRecord(
            case_id="GV-1", address="Addr", category="COMPLETE_VALID",
            language="en", script="latin", source_type="SYNTHETIC",
            expected_status="VERIFIED", predicted_status="VERIFIED", status_matched=True,
            exact_hierarchy_matched=True, expected_ambiguity=False, predicted_ambiguity=False
        )
    ]
    m = BenchmarkMetricsCalculator.evaluate_all(records)
    cm = m["status_classification"]["confusion_matrix"]
    assert len(cm) == 6
    assert "VERIFIED" in cm
    assert "CONSISTENT" in cm
    assert "NEEDS_REVIEW" in cm
    assert "INCONSISTENT" in cm
    assert "AMBIGUOUS" in cm
    assert "UNABLE_TO_VERIFY" in cm


def test_metrics_script_and_category_slicing():
    """Verify slice metrics for script and category."""
    records = [
        EvaluationResultRecord(
            case_id="GV-1", address="Kharadi", category="COMPLETE_VALID",
            language="en", script="latin", source_type="SYNTHETIC",
            expected_status="VERIFIED", predicted_status="VERIFIED", status_matched=True,
            exact_hierarchy_matched=True, expected_ambiguity=False, predicted_ambiguity=False
        ),
        EvaluationResultRecord(
            case_id="GV-2", address="पुणे", category="DEVANAGARI_MARATHI",
            language="mr", script="devanagari", source_type="SYNTHETIC",
            expected_status="VERIFIED", predicted_status="VERIFIED", status_matched=True,
            exact_hierarchy_matched=True, expected_ambiguity=False, predicted_ambiguity=False
        )
    ]
    m = BenchmarkMetricsCalculator.evaluate_all(records)
    assert "latin" in m["script_metrics"]
    assert "devanagari" in m["script_metrics"]
    assert "COMPLETE_VALID" in m["category_metrics"]
    assert "DEVANAGARI_MARATHI" in m["category_metrics"]

