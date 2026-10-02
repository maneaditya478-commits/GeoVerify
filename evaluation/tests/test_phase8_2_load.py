"""Tests for Phase 8.2 Load, Latency Profiler, and Resilience Evaluation Suite."""

import pytest
from evaluation.phase8_2.latency_profiler import LatencyProfiler
from evaluation.phase8_2.concurrency_runner import ConcurrencyRunner
from evaluation.phase8_2.cache_evaluator import CacheEvaluator
from evaluation.phase8_2.failure_injection import FailureInjectionSuite


@pytest.mark.asyncio
async def test_latency_profiler_address_pipeline():
    profiler = LatencyProfiler()
    cases = [
        {"raw_text": "Indiranagar, Bangalore, Karnataka 560038"},
        {"raw_text": "Kothrud, Pune, Maharashtra 411038"},
    ]
    profile = await profiler.profile_address_pipeline(cases)
    assert "normalization" in profile
    assert "candidate_generation" in profile
    assert "dense_retrieval" in profile
    assert "verification_decision" in profile
    assert profile["total_end_to_end"]["mean_ms"] > 0


@pytest.mark.asyncio
async def test_concurrency_runner_text_load():
    runner = ConcurrencyRunner()
    queries = [
        "MG Road, Indiranagar, Bangalore, Karnataka 560038",
        "Shivaji Nagar, Pune, Maharashtra 411005",
    ]
    res = await runner.run_text_load(test_queries=queries, concurrency=5, total_requests=10)
    assert res["workload"] == "text_verification"
    assert res["successful_requests"] == 10
    assert res["failed_requests"] == 0
    assert res["error_rate_pct"] == 0.0
    assert res["throughput_rps"] > 0


def test_cache_evaluator_key_isolation():
    evaluator = CacheEvaluator()
    res = evaluator.evaluate_key_isolation()
    assert res["total_homonym_cases"] > 0
    assert res["collision_free"] is True
    assert res["unique_cache_keys"] == res["total_homonym_cases"]


def test_cache_evaluator_lru_eviction():
    evaluator = CacheEvaluator()
    res = evaluator.evaluate_lru_eviction()
    assert res["capacity_respected"] is True
    assert res["final_cache_size"] <= 10


@pytest.mark.asyncio
async def test_failure_injection_suite():
    suite = FailureInjectionSuite()
    results = await suite.run_full_suite()
    assert len(results) == 4
    assert all(r["passed"] for r in results)
