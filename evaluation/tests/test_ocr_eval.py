"""Unit tests for Phase 7 OCR Evaluation dataset, metrics, and pipeline benchmark."""

import pytest
from evaluation.ocr.dataset import get_ocr_benchmark_cases
from evaluation.ocr.metrics import OCRMetricsCalculator, AggregateOCRBenchmarkResults
from evaluation.ocr.run_ocr_benchmark import generate_synthetic_document_image


def test_ocr_dataset_loading():
    cases = get_ocr_benchmark_cases()
    assert len(cases) >= 15
    
    categories = set(c.category for c in cases)
    assert "clean_documents" in categories
    assert "multilingual_devanagari" in categories
    assert "ocr_noise_substitutions" in categories
    assert "multi_address_documents" in categories
    assert "negative_adversarial" in categories


def test_cer_and_wer_computation():
    ref = "Flat 402, Ganga Carnation, Pune 411014"
    hyp_identical = "Flat 402, Ganga Carnation, Pune 411014"
    hyp_noisy = "Flat 4O2, Ganga Carnatlon, Pune 411014"
    
    assert OCRMetricsCalculator.calculate_cer(ref, hyp_identical) == 0.0
    assert OCRMetricsCalculator.calculate_wer(ref, hyp_identical) == 0.0

    cer_noisy = OCRMetricsCalculator.calculate_cer(ref, hyp_noisy)
    assert 0.0 < cer_noisy < 0.20
    wer_noisy = OCRMetricsCalculator.calculate_wer(ref, hyp_noisy)
    assert 0.0 < wer_noisy <= 0.40


def test_field_matching_logic():
    assert OCRMetricsCalculator.field_match("Pune", "Pune") is True
    assert OCRMetricsCalculator.field_match("411014", "411014") is True
    assert OCRMetricsCalculator.field_match("411014", "411015") is False
    assert OCRMetricsCalculator.field_match("Kharadi", "Kharadi Gaon") is True
    assert OCRMetricsCalculator.field_match(None, None) is True
    assert OCRMetricsCalculator.field_match("Maharashtra", None) is False


def test_synthetic_document_image_generation():
    cases = get_ocr_benchmark_cases()
    case = cases[0]
    img_bytes = generate_synthetic_document_image(case)
    
    assert len(img_bytes) > 100
    assert img_bytes.startswith(b"\x89PNG")


def test_aggregate_benchmark_results():
    agg = AggregateOCRBenchmarkResults()
    agg.total_cases = 2
    agg.cer_scores = [0.02, 0.04]
    agg.wer_scores = [0.05, 0.05]
    agg.region_tp = 2
    agg.field_totals["pincode"] = 2
    agg.field_matches["pincode"] = 2
    agg.verification_status_totals = 2
    agg.verification_status_matches = 2
    agg.latencies_ms = [45.0, 55.0]

    summary = agg.compute_summary()
    assert summary["total_evaluated_cases"] == 2
    assert summary["mean_cer_pct"] == 3.0
    assert summary["field_extraction_accuracy"]["pincode"] == 100.0
    assert summary["verification_status_accuracy_pct"] == 100.0
    assert summary["latency_ms"]["mean"] == 50.0
