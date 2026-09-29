"""Evaluation tests for Phase 8 evaluation harness and stress benchmarks."""

import pytest
from evaluation.phase8.stress_dataset import get_phase8_stress_dataset
from evaluation.phase8.top1_analyzer import Top1FailureAnalyzer
from evaluation.phase8.ocr_quality_runner import OCRQualityCurveRunner
from evaluation.phase8.retrieval_ablation import RetrievalChannelAblationRunner
from evaluation.phase8.homonymous_auditor import HomonymousLocalityAuditor
from evaluation.phase8.ablation_runner import Phase8AblationRunner


class TestPhase8EvaluationSuite:
    """Validates Phase 8 stress suite and ablation engines."""

    def test_stress_dataset_structure(self):
        dataset = get_phase8_stress_dataset()
        assert len(dataset) == 120
        categories = {c["category"] for c in dataset}
        assert "dpi_degradation" in categories
        assert "skew_degradation" in categories
        assert "multilingual_devanagari" in categories
        assert "homonymous_locality" in categories

    def test_top1_analyzer(self):
        dataset = get_phase8_stress_dataset()[:10]
        analyzer = Top1FailureAnalyzer()
        failures = analyzer.analyze_cases(dataset)
        assert isinstance(failures, list)

    def test_ocr_quality_curve_runner(self):
        dataset = get_phase8_stress_dataset()
        runner = OCRQualityCurveRunner()
        records = runner.evaluate_quality_curve(dataset)
        assert len(records) > 0
        assert any(r["dimension"] == "DPI" for r in records)
        assert any(r["dimension"] == "SKEW_ANGLE" for r in records)

    def test_retrieval_channel_ablation_runner(self):
        dataset = get_phase8_stress_dataset()[:5]
        runner = RetrievalChannelAblationRunner()
        records = runner.run_ablation(dataset)
        assert len(records) == 10
        assert any(r["channel_configuration"] == "Full_Ensemble_All_Channels" for r in records)

    def test_homonymous_auditor(self):
        dataset = [c for c in get_phase8_stress_dataset() if c["category"] == "homonymous_locality"][:6]
        auditor = HomonymousLocalityAuditor()
        records = auditor.audit_cases(dataset)
        assert len(records) == 6
        assert any(r["expected_status"] == "AMBIGUOUS" for r in records)

    def test_ablation_runner(self):
        runner = Phase8AblationRunner()
        results = runner.run_all_ablations()
        assert "EXP_A_Baseline" in results
        assert "EXP_F_Full_Phase8_Stack" in results
        assert "EXP_G_Ambiguity_Calibration" in results
        assert results["EXP_F_Full_Phase8_Stack"]["recall_at_1"] > results["EXP_A_Baseline"]["recall_at_1"]
