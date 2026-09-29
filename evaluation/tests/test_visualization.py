"""Unit tests for Visualizer chart generator."""

import pytest
from pathlib import Path
from evaluation.visualization import Visualizer
from evaluation.schema import EvaluationResultRecord


def test_visualizer_generate_all_charts(tmp_path: Path):
    """Verify Visualizer generates all 7 charts in specified directory."""
    metrics = {
        "entity_resolution": {
            "state_accuracy": 0.95,
            "district_accuracy": 0.92,
            "subdistrict_accuracy": 0.88,
            "locality_accuracy": 0.86,
            "pincode_accuracy": 0.98,
            "exact_hierarchy_accuracy": 0.85
        },
        "script_metrics": {
            "latin": {"exact_hierarchy_acc": 0.88, "status_acc": 0.89, "mean_latency_ms": 3.2},
            "devanagari": {"exact_hierarchy_acc": 0.82, "status_acc": 0.85, "mean_latency_ms": 3.8},
            "mixed": {"exact_hierarchy_acc": 0.80, "status_acc": 0.84, "mean_latency_ms": 4.1}
        },
        "category_metrics": {
            "COMPLETE_VALID": {"status_acc": 0.98, "exact_hierarchy_acc": 0.95, "mean_consistency_score": 94.0},
            "DISTRICT_MISMATCH": {"status_acc": 0.92, "exact_hierarchy_acc": 0.90, "mean_consistency_score": 35.0}
        },
        "status_classification": {
            "confusion_matrix": {
                "VERIFIED": {"VERIFIED": 80, "CONSISTENT": 5, "NEEDS_REVIEW": 2, "INCONSISTENT": 0, "AMBIGUOUS": 0, "UNABLE_TO_VERIFY": 0},
                "CONSISTENT": {"VERIFIED": 2, "CONSISTENT": 40, "NEEDS_REVIEW": 5, "INCONSISTENT": 0, "AMBIGUOUS": 0, "UNABLE_TO_VERIFY": 0},
                "NEEDS_REVIEW": {"VERIFIED": 0, "CONSISTENT": 1, "NEEDS_REVIEW": 30, "INCONSISTENT": 2, "AMBIGUOUS": 0, "UNABLE_TO_VERIFY": 0},
                "INCONSISTENT": {"VERIFIED": 0, "CONSISTENT": 0, "NEEDS_REVIEW": 1, "INCONSISTENT": 50, "AMBIGUOUS": 0, "UNABLE_TO_VERIFY": 0},
                "AMBIGUOUS": {"VERIFIED": 0, "CONSISTENT": 0, "NEEDS_REVIEW": 0, "INCONSISTENT": 0, "AMBIGUOUS": 25, "UNABLE_TO_VERIFY": 0},
                "UNABLE_TO_VERIFY": {"VERIFIED": 0, "CONSISTENT": 0, "NEEDS_REVIEW": 1, "INCONSISTENT": 0, "AMBIGUOUS": 0, "UNABLE_TO_VERIFY": 20}
            }
        },
        "component_performance": {
            "components": {
                "address_normalizer": {"p50_ms": 0.2, "p95_ms": 0.5, "p99_ms": 0.8},
                "indic_transliteration": {"p50_ms": 0.3, "p95_ms": 0.7, "p99_ms": 1.0},
                "address_parser": {"p50_ms": 0.4, "p95_ms": 0.9, "p99_ms": 1.2},
                "entity_resolution": {"p50_ms": 1.1, "p95_ms": 2.2, "p99_ms": 3.0},
                "verification_engine_pipeline": {"p50_ms": 2.5, "p95_ms": 4.5, "p99_ms": 6.0}
            }
        }
    }

    results = [
        EvaluationResultRecord(
            case_id="GV-1", address="Valid", category="COMPLETE_VALID",
            language="en", script="latin", source_type="SYNTHETIC",
            expected_status="VERIFIED", predicted_status="VERIFIED", status_matched=True,
            exact_hierarchy_matched=True, expected_ambiguity=False, predicted_ambiguity=False,
            completeness_score=90, consistency_score=94
        )
    ]

    Visualizer.generate_all_charts(metrics, results, tmp_path)

    expected_files = [
        "hierarchy_accuracy.png",
        "category_performance.png",
        "script_language_accuracy.png",
        "completeness_vs_accuracy.png",
        "confusion_matrix.png",
        "latency_distribution.png",
        "error_distribution.png"
    ]

    for fname in expected_files:
        f = tmp_path / fname
        assert f.exists()
        assert f.stat().st_size > 1000
