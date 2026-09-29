"""Unit tests for Phase 7.3 Diagnostic, Calibration, and Evaluation Modules."""

import pytest
from evaluation.phase7_3.decision_trace import StructuredDecisionTrace
from evaluation.phase7_3.same_resolution_audit import SameResolutionAuditor, SameResolutionGapCase
from evaluation.phase7_3.needs_review_auditor import NeedsReviewAuditor, NeedsReviewSummary
from evaluation.phase7_3.provenance_auditor import ProvenanceStrengthAuditor, ProvenanceChannelMetric
from evaluation.phase7_3.score_distribution_auditor import ScoreDistributionAuditor, ScoreBandMetric
from evaluation.phase7_3.rule_auditor import DecisionRuleAuditor, RuleTriggerMetric
from evaluation.phase7_3.ocr_gap_decomposer import OCRGapDecomposer, GapAttributionRow
from evaluation.phase7_3.ablation_runner import Phase73AblationRunner, AblationExperimentResult


def test_structured_decision_trace_serialization():
    trace = StructuredDecisionTrace(
        case_id="TRACE_001",
        input_type="ocr_document",
        raw_input="Flat 1, Kharadi, Pune, Maharashtra 411014",
        extracted_fields={"locality": "Kharadi", "district": "Pune", "pincode": "411014"},
        final_score=88.5,
        final_status="VERIFIED",
        ground_truth_status="VERIFIED",
        correct=True,
    )
    d = trace.to_dict()
    assert d["case_id"] == "TRACE_001"
    assert d["final_status"] == "VERIFIED"
    assert d["correct"] is True
    assert d["final_score"] == 88.5


def test_same_resolution_auditor():
    clean_res = {"status": "VERIFIED", "score": 92.0, "top_candidate": "Kharadi", "fields": {"locality": "Kharadi", "district": "Pune", "pincode": "411014"}, "rules": ["LOCALITY_VERIFIED"]}
    ocr_res = {"status": "NEEDS_REVIEW", "score": 68.0, "top_candidate": "Kharadi", "fields": {"locality": "Kharadi", "pincode": "411014"}, "rules": ["DISTRICT_MISSING"], "provenance": {"locality": "EXPLICIT"}}
    
    gap_case = SameResolutionAuditor.audit_case(
        case_id="GAP_001",
        clean_res=clean_res,
        ocr_res=ocr_res,
        ground_truth={"expected_status": "VERIFIED"},
    )
    assert gap_case is not None
    assert gap_case.case_id == "GAP_001"
    assert gap_case.candidate_same is True
    assert gap_case.clean_status == "VERIFIED"
    assert gap_case.ocr_status == "NEEDS_REVIEW"
    assert gap_case.score_delta == -24.0


def test_needs_review_auditor():
    cases_data = [
        {"case_id": "NR_01", "category": "clean", "expected_status": "NEEDS_REVIEW", "predicted_status": "NEEDS_REVIEW", "score": 65.0, "triggered_rules": ["RULE_POSTAL_OR_LOW_SCORE_REVIEW"]},
        {"case_id": "NR_02", "category": "clean", "expected_status": "VERIFIED", "predicted_status": "VERIFIED", "score": 90.0, "triggered_rules": ["RULE_HIGH_CONFIDENCE_VERIFIED"]},
        {"case_id": "NR_03", "category": "clean", "expected_status": "VERIFIED", "predicted_status": "NEEDS_REVIEW", "score": 58.0, "triggered_rules": ["NO_COORDINATES"]},
    ]
    summary = NeedsReviewAuditor.audit_cases(cases_data)
    assert summary.total_evaluated == 3
    assert summary.true_positive_count == 1
    assert summary.false_positive_count == 1
    assert summary.precision == 50.0


def test_provenance_strength_auditor():
    cases_data = [
        {"field_provenance": {"locality": {"method": "EXPLICIT"}, "pincode": {"method": "OCR_REPAIRED"}}, "correct": True, "predicted_status": "VERIFIED"},
        {"field_provenance": {"state": {"method": "PIN_RECOVERY"}}, "correct": True, "predicted_status": "CONSISTENT"},
    ]
    metrics = ProvenanceStrengthAuditor.audit_provenance_channels(cases_data)
    assert len(metrics) == 7
    channel_names = {m.channel_name for m in metrics}
    assert "EXPLICIT" in channel_names
    assert "PIN_RECOVERY" in channel_names
    assert "OCR_REPAIRED" in channel_names


def test_score_distribution_auditor():
    cases_data = [
        {"score": 95.0, "correct": True, "predicted_status": "VERIFIED"},
        {"score": 75.0, "correct": True, "predicted_status": "CONSISTENT"},
        {"score": 50.0, "correct": False, "predicted_status": "NEEDS_REVIEW"},
        {"score": 15.0, "correct": True, "predicted_status": "INCONSISTENT"},
    ]
    metrics = ScoreDistributionAuditor.audit_scores(cases_data)
    assert len(metrics) == 6
    band_85 = next(m for m in metrics if m.band_name == "85-100")
    assert band_85.support == 1
    assert band_85.correct_count == 1


def test_decision_rule_auditor():
    cases_data = [
        {"triggered_rules": ["RULE_HIGH_CONFIDENCE_VERIFIED", "STATE_VERIFIED"], "correct": True, "predicted_status": "VERIFIED"},
        {"triggered_rules": ["RULE_CONSISTENT_STANDARD"], "correct": True, "predicted_status": "CONSISTENT"},
    ]
    metrics = DecisionRuleAuditor.audit_rules(cases_data)
    assert len(metrics) >= 6
    state_rule = next((m for m in metrics if m.rule_name == "STATE_VERIFIED"), None)
    assert state_rule is not None
    assert state_rule.trigger_count == 1


def test_ocr_gap_decomposer():
    paired_data = [
        {"clean_status_match": True, "ocr_status_match": False, "root_cause": "OCR_ERROR"},
        {"clean_status_match": True, "ocr_status_match": False, "root_cause": "PIN_ERROR"},
        {"clean_status_match": True, "ocr_status_match": True, "root_cause": "NONE"},
    ]
    rows = OCRGapDecomposer.decompose_gap(86.25, 76.25, paired_data)
    assert len(rows) > 0
    total_cases = sum(r.cases for r in rows)
    assert total_cases == 2


def test_ablation_runner():
    ablations = Phase73AblationRunner.run_all_ablations({})
    assert len(ablations) == 6
    exp_ids = {a.experiment_id for a in ablations}
    assert "EXP_A_BASELINE" in exp_ids
    assert "EXP_F_COMBINED_PHASE7_3" in exp_ids
    f_model = next(a for a in ablations if a.experiment_id == "EXP_F_COMBINED_PHASE7_3")
    assert f_model.clean_ocr_gap_pct < 8.0
