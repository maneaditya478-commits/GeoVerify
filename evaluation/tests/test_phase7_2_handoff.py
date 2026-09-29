"""Unit tests for Phase 7.2 Handoff Validation, Regression Audit, Telemetry, and Evaluation Modules."""

import pytest
from evaluation.phase7_2.dataset import (
    get_phase7_2_benchmark_cases,
    Split,
    OCRTestCase,
)
from evaluation.phase7_2.pipeline_trace import (
    StagedPipelineTrace,
    PipelineTracer,
)
from evaluation.phase7_2.error_classifier import (
    EarliestFailureClassifier,
    FailureStageClass,
    CaseFailureDiagnosis,
)
from evaluation.phase7_2.decision_audit import (
    DecisionEngineAuditor,
    STATUS_CLASSES,
    SCORE_BANDS,
)
from evaluation.phase7_2.multilingual_handoff import MultilingualHandoffAnalyzer
from evaluation.phase7_2.profile_pipeline import LatencyProfiler
from evaluation.phase7_2.provenance_audit import ProvenanceAuditor


def test_phase7_2_dataset_size_and_splits():
    """Verify that the 260 cases match exact 60/20/20 split constraints."""
    all_cases = get_phase7_2_benchmark_cases()
    assert len(all_cases) == 260

    dev_cases = get_phase7_2_benchmark_cases(Split.DEV)
    val_cases = get_phase7_2_benchmark_cases(Split.VAL)
    held_out_cases = get_phase7_2_benchmark_cases(Split.HELD_OUT)

    assert len(dev_cases) == 156
    assert len(val_cases) == 52
    assert len(held_out_cases) == 52
    assert len(dev_cases) + len(val_cases) + len(held_out_cases) == 260


def test_phase7_2_dataset_categories():
    """Ensure all 8 required categories are present."""
    all_cases = get_phase7_2_benchmark_cases()
    categories = {c.category for c in all_cases}
    expected_categories = {
        "clean_documents",
        "multilingual_devanagari",
        "scan_degradations",
        "ocr_noise_substitutions",
        "complex_multi_address",
        "multi_token_localities",
        "partial_and_rural",
        "negative_adversarial",
    }
    assert categories == expected_categories


def test_pipeline_trace_structure():
    """Ensure StagedPipelineTrace captures stages properly."""
    trace = StagedPipelineTrace(
        case_id="TEST_001",
        ground_truth={"state": "Maharashtra", "district": "Pune", "locality": "Kharadi", "pincode": "411014"},
        ocr={"status": "SUCCESS", "engine": "MOCK_OCR", "mean_confidence": 0.95},
        normalized_text="flat 1, kharadi, pune, maharashtra 411014",
        extracted_fields={"pincode": "411014", "district": "Pune", "locality": "Kharadi", "state": "Maharashtra"},
        assembled_address="Kharadi, Pune, Maharashtra 411014",
        candidate_generation={"top_candidate": "Kharadi"},
        final_status={"status": "VERIFIED", "score": 0.95},
    )

    assert trace.case_id == "TEST_001"
    assert trace.final_status["status"] == "VERIFIED"
    assert trace.extracted_fields["pincode"] == "411014"


def test_earliest_failure_classifier_clean_success():
    """Success trace diagnosis returns NONE failure class."""
    trace = StagedPipelineTrace(
        case_id="TEST_002",
        ground_truth={"state": "Maharashtra", "district": "Pune", "locality": "Kharadi", "pincode": "411014"},
        extracted_fields={"pincode": "411014", "district": "Pune", "locality": "Kharadi", "state": "Maharashtra"},
        assembled_address="Kharadi, Pune, Maharashtra 411014",
        candidate_generation={"top_candidate": "Kharadi"},
        final_status={"status": "VERIFIED", "score": 0.92},
    )

    diagnosis = EarliestFailureClassifier.classify_trace(trace, is_negative=False)
    assert diagnosis.is_failure is False
    assert diagnosis.earliest_error == FailureStageClass.NONE


def test_earliest_failure_classifier_field_extraction_error():
    """Mismatched district field triggers FIELD_EXTRACTION_ERROR."""
    trace = StagedPipelineTrace(
        case_id="TEST_003",
        ground_truth={"state": "Maharashtra", "district": "Pune", "pincode": "411014"},
        extracted_fields={"pincode": "411014", "district": "Thane", "state": "Maharashtra"},
        assembled_address="Kharadi, Thane, Maharashtra 411014",
        final_status={"status": "VERIFIED", "score": 0.90},
    )

    diagnosis = EarliestFailureClassifier.classify_trace(trace, is_negative=False)
    assert diagnosis.is_failure is True
    assert diagnosis.earliest_error == FailureStageClass.FIELD_EXTRACTION_ERROR


def test_decision_engine_auditor():
    """Verify confusion matrix calculations and metric validity."""
    gt = ["VERIFIED", "VERIFIED", "CONSISTENT", "INCONSISTENT"]
    pred = ["VERIFIED", "VERIFIED", "CONSISTENT", "INCONSISTENT"]
    scores = [0.95, 0.90, 0.82, 0.30]
    rules = [["RULE_VERIFIED"], ["RULE_VERIFIED"], ["RULE_CONSISTENT"], ["RULE_INCONSISTENT"]]

    summary = DecisionEngineAuditor.audit_decisions(gt, pred, scores, rules)
    assert summary.total_evaluated == 4
    assert summary.accuracy_pct == 100.0
    assert 0.0 <= summary.macro_f1 <= 100.0
    assert 0.0 <= summary.weighted_f1 <= 100.0


def test_multilingual_handoff_analyzer():
    """Verify script and language stratification."""
    paired_data = [
        {
            "language": "mar",
            "script": "Devanagari",
            "clean_locality_match": True,
            "ocr_locality_match": True,
            "clean_district_match": True,
            "ocr_district_match": True,
            "clean_status_match": True,
            "ocr_status_match": True,
            "same_resolution": True,
        },
        {
            "language": "eng",
            "script": "Latin",
            "clean_locality_match": True,
            "ocr_locality_match": True,
            "clean_district_match": True,
            "ocr_district_match": True,
            "clean_status_match": True,
            "ocr_status_match": True,
            "same_resolution": True,
        },
    ]

    rows = MultilingualHandoffAnalyzer.evaluate_strata(paired_data)
    assert len(rows) == 2
    languages = {r.language for r in rows}
    assert "mar" in languages
    assert "eng" in languages


def test_latency_profiler():
    """Verify latency profiling stats."""
    stage_records = {
        "ocr_execution": [15.0, 25.0],
        "entity_resolution": [5.0, 7.0],
    }
    total_latencies = [20.0, 32.0]

    metrics = LatencyProfiler.compute_stage_latencies(stage_records, total_latencies)
    assert len(metrics) > 0
    ocr_metric = next((m for m in metrics if m.stage_name == "ocr_execution"), None)
    assert ocr_metric is not None
    assert ocr_metric.mean_ms == 20.0


def test_provenance_auditor():
    """Verify provenance audit logic and ablation structure."""
    mock_data = [{"dummy": 1}]
    ablation_rows = ProvenanceAuditor.evaluate_provenance_ablation(mock_data)
    assert len(ablation_rows) >= 4
    configs = {r.configuration_name for r in ablation_rows}
    assert "EXPLICIT only" in configs
    assert any("FULL" in c for c in configs)
