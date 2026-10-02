"""Evaluation suite tests for Phase 8.3 Production Reliability, Golden Regression & Chaos."""

import pytest
from evaluation.phase8_3.golden_regression import GoldenRegressionEvaluator
from evaluation.phase8_3.soak_runner import SoakTestRunner
from evaluation.phase8_3.cache_security_auditor import CacheSecurityAuditor
from evaluation.phase8_3.failure_injection_suite import FailureInjectionSuite
from evaluation.phase8_3.concurrency_capacity_planner import ConcurrencyCapacityPlanner
from evaluation.phase8_3.security_auditor import SecurityAuditor
from evaluation.phase8_3.recovery_runner import RecoveryRunner


@pytest.mark.asyncio
async def test_golden_regression_suite_pass():
    evaluator = GoldenRegressionEvaluator()
    res = await evaluator.run_evaluation()
    assert res["all_invariants_passed"] is True
    assert res["accuracy_pct"] == 100.0


@pytest.mark.asyncio
async def test_soak_runner_execution():
    runner = SoakTestRunner()
    res = await runner.run_soak(duration_seconds=2.0, concurrency=5)
    assert res["total_requests"] > 0
    assert res["error_rate_pct"] == 0.0
    assert res["memory"]["verdict"] in ["STABLE", "INVESTIGATE"]


@pytest.mark.asyncio
async def test_cache_security_auditor_full():
    auditor = CacheSecurityAuditor()
    res = await auditor.run_full_audit()
    assert res["overall_cache_integrity_passed"] is True


@pytest.mark.asyncio
async def test_failure_injection_matrix():
    suite = FailureInjectionSuite()
    results = await suite.run_full_suite()
    assert len(results) == 5
    assert all(r["passed"] for r in results)


@pytest.mark.asyncio
async def test_concurrency_capacity_bench():
    planner = ConcurrencyCapacityPlanner()
    res = await planner.benchmark_concurrency_level(concurrency=5, total_requests=10)
    assert res["successful_requests"] == 10
    assert res["error_rate_pct"] == 0.0
    assert res["throughput_rps"] > 0


def test_security_auditor_source_and_privacy():
    auditor = SecurityAuditor()
    report = auditor.run_full_security_audit()
    assert report["security_audit_verdict"] == "PASS"
    assert report["source_code_safety"]["passed"] is True
    assert report["logging_privacy"]["passed"] is True


@pytest.mark.asyncio
async def test_recovery_lifecycle_suite():
    runner = RecoveryRunner()
    report = await runner.run_recovery_suite()
    assert report["overall_recovery_passed"] is True
