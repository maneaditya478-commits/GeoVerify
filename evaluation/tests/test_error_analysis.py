"""Unit tests for ErrorAnalyzer."""

import pytest
from evaluation.schema import EvaluationResultRecord
from evaluation.error_analysis import ErrorAnalyzer


def test_classify_error_ambiguity():
    """Verify classification of ambiguity error."""
    rec = EvaluationResultRecord(
        case_id="GV-ERR-1",
        address="Rampur",
        category="AMBIGUOUS_LOCALITY",
        language="en",
        script="latin",
        source_type="SYNTHETIC",
        expected_status="AMBIGUOUS",
        predicted_status="CONSISTENT",
        status_matched=False,
        expected_ambiguity=True,
        predicted_ambiguity=False,
        ambiguity_matched=False
    )
    err = ErrorAnalyzer.classify_error(rec)
    assert err == "AMBIGUITY"


def test_classify_error_pin_mismatch():
    """Verify classification of PIN mismatch error."""
    rec = EvaluationResultRecord(
        case_id="GV-ERR-2",
        address="Kharadi, Pune, Maharashtra 560066",
        category="PIN_MISMATCH",
        language="en",
        script="latin",
        source_type="SYNTHETIC",
        expected_status="NEEDS_REVIEW",
        predicted_status="VERIFIED",
        status_matched=False,
        expected_ambiguity=False,
        predicted_ambiguity=False
    )
    err = ErrorAnalyzer.classify_error(rec)
    assert err == "PIN_MISMATCH"


def test_analyze_errors_summary():
    """Verify analyze_errors returns list of failures and category counts."""
    records = [
        EvaluationResultRecord(
            case_id="GV-1", address="Valid Address", category="COMPLETE_VALID",
            language="en", script="latin", source_type="SYNTHETIC",
            expected_status="VERIFIED", predicted_status="VERIFIED", status_matched=True,
            exact_hierarchy_matched=True, expected_ambiguity=False, predicted_ambiguity=False
        ),
        EvaluationResultRecord(
            case_id="GV-2", address="Mismatch Address", category="DISTRICT_MISMATCH",
            language="en", script="latin", source_type="SYNTHETIC",
            expected_status="INCONSISTENT", predicted_status="VERIFIED", status_matched=False,
            exact_hierarchy_matched=False, expected_ambiguity=False, predicted_ambiguity=False
        )
    ]
    errors, counts = ErrorAnalyzer.analyze_errors(records)
    assert len(errors) == 1
    assert "ADMINISTRATIVE_MISMATCH" in counts
    assert counts["ADMINISTRATIVE_MISMATCH"] == 1
