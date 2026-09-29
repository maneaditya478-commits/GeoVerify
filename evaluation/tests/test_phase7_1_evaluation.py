"""Unit tests for Phase 7.1 diagnostic, error matrix, calibration, and benchmark evaluation modules."""

import pytest
from evaluation.phase7_1.dataset import (
    get_phase7_1_benchmark_cases,
    Split,
)
from evaluation.phase7_1.error_matrix import (
    ErrorMatrixAnalyzer,
    FailureRootCause,
    PipelineFailureStage,
)
from evaluation.phase7_1.field_analysis import FieldAnalysisAuditor
from evaluation.phase7_1.multilingual_analysis import MultilingualAnalyzer
from evaluation.phase7_1.confidence_calibration import ConfidenceCalibrationAnalyzer
from evaluation.phase7_1.ocr_degradation_analysis import OCRDegradationAnalyzer
from evaluation.phase7_1.ablation import PipelineAblationRunner


def test_phase7_1_dataset_splits_and_size():
    all_cases = get_phase7_1_benchmark_cases()
    assert len(all_cases) >= 100

    dev_cases = get_phase7_1_benchmark_cases(Split.DEV)
    val_cases = get_phase7_1_benchmark_cases(Split.VAL)
    held_out_cases = get_phase7_1_benchmark_cases(Split.HELD_OUT)

    assert len(dev_cases) + len(val_cases) + len(held_out_cases) == len(all_cases)
    # Check 60/20/20 approximate proportions
    assert 55 <= len(dev_cases) <= 70
    assert 18 <= len(val_cases) <= 25
    assert 18 <= len(held_out_cases) <= 25


def test_error_matrix_diagnosis_logic():
    # True positive case with no errors
    diag_clean = ErrorMatrixAnalyzer.diagnose_case(
        case_id="C1",
        is_negative=False,
        doc_cer=0.0,
        region_detected=True,
        extracted_fields={"pincode": "411014", "district": "Pune", "locality": "Kharadi"},
        ground_truth={"pincode": "411014", "district": "Pune", "locality": "Kharadi"},
        actual_status="VERIFIED",
        expected_status="VERIFIED",
    )
    assert diag_clean.is_failure is False
    assert diag_clean.root_cause == FailureRootCause.NONE

    # District extraction mismatch
    diag_dist = ErrorMatrixAnalyzer.diagnose_case(
        case_id="C2",
        is_negative=False,
        doc_cer=0.0,
        region_detected=True,
        extracted_fields={"pincode": "411014", "district": "Thane", "locality": "Kharadi"},
        ground_truth={"pincode": "411014", "district": "Pune", "locality": "Kharadi"},
        actual_status="VERIFIED",
        expected_status="VERIFIED",
    )
    assert diag_dist.is_failure is True
    assert diag_dist.root_cause == FailureRootCause.DISTRICT_EXTRACTION_ERROR
    assert diag_dist.earliest_failure_stage == PipelineFailureStage.FIELD_EXTRACTOR


def test_field_analysis_auditor():
    # Audit district omission
    d_rec = FieldAnalysisAuditor.audit_district_error(
        case_id="C1",
        category="clean_documents",
        expected="Pune",
        extracted=None,
        raw_text="Flat 1, Kharadi 411014",
    )
    assert d_rec is not None
    assert d_rec.error_type == "OMISSION"

    # Audit valid locality match
    l_rec = FieldAnalysisAuditor.audit_locality_error(
        case_id="C1",
        category="clean_documents",
        expected="Kharadi",
        extracted="Kharadi Gaon",
        raw_text="Flat 1, Kharadi Gaon 411014",
    )
    assert l_rec is None


def test_confidence_calibration_analyzer():
    confidences = [0.95, 0.90, 0.85, 0.40, 0.15]
    outcomes = [True, True, True, False, False]

    report = ConfidenceCalibrationAnalyzer.evaluate_calibration(confidences, outcomes)
    assert report.total_samples == 5
    assert len(report.buckets) == 5
    assert 0.0 <= report.expected_calibration_error_pct <= 100.0
    assert 0.0 <= report.brier_score <= 1.0


def test_multilingual_analyzer_strata():
    cases = [
        {"language": "hin", "script": "Devanagari", "region_tp": True, "pincode_match": True, "state_match": True, "district_match": True, "locality_match": True, "status_match": True},
        {"language": "hin", "script": "Devanagari", "region_tp": True, "pincode_match": True, "state_match": True, "district_match": False, "locality_match": True, "status_match": True},
        {"language": "eng", "script": "Latin", "region_tp": True, "pincode_match": True, "state_match": True, "district_match": True, "locality_match": True, "status_match": True},
    ]
    res = MultilingualAnalyzer.evaluate_strata(cases)
    assert "hin_Devanagari" in res
    assert "eng_Latin" in res
    assert res["hin_Devanagari"].total_cases == 2
    assert res["hin_Devanagari"].district_accuracy == 50.0


def test_degradation_analyzer():
    clean_evals = [{"case_id": "C1", "recall_at_1": True, "district_match": True, "locality_match": True, "status_match": True}]
    ocr_evals = [{"case_id": "C1", "recall_at_1": True, "district_match": True, "locality_match": False, "status_match": True}]

    report = OCRDegradationAnalyzer.analyze_degradation(clean_evals, ocr_evals)
    assert report.total_compared_cases == 1
    assert report.locality_accuracy_delta.degradation_delta == -100.0


def test_ablation_runner():
    cases = get_phase7_1_benchmark_cases()
    report = PipelineAblationRunner.evaluate_ablation_suite(cases)
    assert len(report.ablation_steps) == 6
    assert report.ablation_steps[0].step_id == "A0"
    assert report.ablation_steps[-1].step_id == "A5"
    assert report.ablation_steps[-1].pincode_accuracy_pct > report.ablation_steps[0].pincode_accuracy_pct
