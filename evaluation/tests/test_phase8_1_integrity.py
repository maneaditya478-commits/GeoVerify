"""Evaluation tests for Phase 8.1 splits, manifest, and attribution modules."""

import pytest
from pathlib import Path

from evaluation.phase8_1.manifest import ExperimentManifest
from evaluation.phase8_1.splits import get_dev_split, get_validation_split, get_heldout_split
from evaluation.phase8_1.component_attribution import ComponentAttributionEngine
from evaluation.phase8_1.top1_taxonomy import Top1TaxonomyAnalyzer
from evaluation.phase8_1.homonym_auditor import HomonymDisambiguationAuditor
from evaluation.phase8_1.statistical_validator import StatisticalValidator
from evaluation.phase8_1.leakage_auditor import DataLeakageAuditor


class TestPhase81EvaluationIntegrity:
    """Validates split isolation, manifest hashing, and statistical validation."""

    def test_split_isolation_and_no_overlap(self):
        dev = get_dev_split()
        val = get_validation_split()
        heldout = get_heldout_split()

        assert len(dev) == 60
        assert len(val) == 60
        assert len(heldout) == 60

        dev_ids = {c["id"] for c in dev}
        val_ids = {c["id"] for c in val}
        heldout_ids = {c["id"] for c in heldout}

        # Zero intersection across splits
        assert len(dev_ids & val_ids) == 0
        assert len(dev_ids & heldout_ids) == 0
        assert len(val_ids & heldout_ids) == 0

    def test_manifest_generation(self):
        manifest = ExperimentManifest.create_run_manifest(
            experiment_id="TEST_RUN",
            split="dev",
            features_enabled=["ENABLE_DENSE_RETRIEVAL"],
            dataset_files=[],
        )
        assert manifest["experiment_id"] == "TEST_RUN"
        assert manifest["git_commit"] == "901246f"

    def test_component_attribution_engine(self):
        val = get_validation_split()[:5]
        engine = ComponentAttributionEngine()
        records = engine.analyze_split(val)
        assert len(records) == 5
        assert all("primary_recovery_component" in r for r in records)

    def test_top1_taxonomy_analyzer(self):
        val = get_validation_split()[:5]
        analyzer = Top1TaxonomyAnalyzer()
        records = analyzer.analyze_split(val)
        assert isinstance(records, list)

    def test_homonym_auditor_denominators(self):
        auditor = HomonymDisambiguationAuditor()
        stats = auditor.audit_homonym_cases_with_denominators()
        assert stats["total_homonym_cases"] == 48
        assert stats["false_confidence_rate_pct"] == 0.00
        assert stats["resolution_accuracy_pct"] == 100.00

    def test_statistical_validator_wilson_ci(self):
        pt, lo, hi = StatisticalValidator.compute_wilson_ci(106, 120)
        assert 80.0 < lo < pt < hi < 95.0

    def test_leakage_auditor_passes(self):
        auditor = DataLeakageAuditor()
        audit_res = auditor.run_leakage_audit()
        assert audit_res["overall_status"] == "PASS"
        assert audit_res["benchmark_id_leakage"] is False
