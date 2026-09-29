"""Unit tests for PerformanceProfiler and timing utilities."""

import pytest
from evaluation.performance import PerformanceProfiler


def test_performance_profiler_compute_stats():
    """Verify statistics computation from latencies."""
    latencies = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    stats = PerformanceProfiler._compute_stats(latencies)
    assert stats["mean_ms"] == 5.5
    assert stats["median_ms"] == 5.5
    assert stats["min_ms"] == 1.0
    assert stats["max_ms"] == 10.0
    assert stats["p50_ms"] == 5.5
    assert stats["p95_ms"] > 9.0


def test_performance_profiler_empty():
    """Verify empty latency list returns empty dict."""
    assert PerformanceProfiler._compute_stats([]) == {}


@pytest.mark.asyncio
async def test_performance_profiler_benchmark_components_smoke():
    """Verify smoke run of component timing profiler."""
    res = await PerformanceProfiler.benchmark_components(repetitions=2)
    assert "components" in res
    assert "address_normalizer" in res["components"]
    assert "entity_resolution" in res["components"]
    assert "verification_engine_pipeline" in res["components"]
    assert res["components"]["address_normalizer"]["mean_ms"] >= 0
