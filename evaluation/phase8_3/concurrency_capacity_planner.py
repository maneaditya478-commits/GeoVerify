"""Phase 8.3 Concurrency Capacity Planning & Saturation Profiler.

Evaluates system throughput, latency distribution, and saturation across:
1, 5, 10, 25, 50, 100, and 200 concurrent workers.

Identifies:
- Peak RPS (maximum throughput achieved)
- Sustainable RPS (maximum throughput satisfying P95 <= 150ms and Error Rate <= 0.01%)
- Saturation Point (point of diminishing returns or queue congestion)
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
import numpy as np

from app.schemas.address import VerificationRequest
from app.verification.engine import VerificationEngine


class ConcurrencyCapacityPlanner:
    """Evaluates concurrency scaling curves and operational capacity limits."""

    def __init__(self):
        self.engine = VerificationEngine()
        self.test_corpus = [
            "MG Road, Indiranagar, Bangalore, Karnataka 560038",
            "Shivaji Nagar, Pune, Maharashtra 411005",
            "Connaught Place, New Delhi, Delhi 110001",
            "Anna Salai, Chennai, Tamil Nadu 600002",
            "Salt Lake Sector 5, Kolkata, West Bengal 700091",
            "Banjara Hills Road 12, Hyderabad, Telangana 500034",
            "Kothrud, Pune, Maharashtra 411038",
            "Navrangpura, Ahmedabad, Gujarat 380009",
        ]

    async def benchmark_concurrency_level(
        self,
        concurrency: int,
        total_requests: int = 100,
    ) -> Dict[str, Any]:
        """Runs a batch of requests under fixed concurrency and records metrics."""
        latencies: List[float] = []
        errors: int = 0
        semaphore = asyncio.Semaphore(concurrency)

        async def worker(idx: int):
            nonlocal errors
            query = self.test_corpus[idx % len(self.test_corpus)]
            req = VerificationRequest(address=query)
            async with semaphore:
                t0 = time.perf_counter()
                try:
                    res = await self.engine.verify(req)
                    dt = (time.perf_counter() - t0) * 1000.0
                    latencies.append(dt)
                except Exception:
                    errors += 1

        t_start = time.perf_counter()
        tasks = [asyncio.create_task(worker(i)) for i in range(total_requests)]
        await asyncio.gather(*tasks)
        duration = time.perf_counter() - t_start

        arr = np.array(latencies) if latencies else np.array([0.0])
        rps = total_requests / duration if duration > 0 else 0.0
        error_rate = (errors / total_requests * 100.0) if total_requests else 0.0

        p95 = float(np.percentile(arr, 95))
        is_sustainable = (p95 <= 150.0) and (error_rate == 0.0)

        return {
            "concurrency": concurrency,
            "total_requests": total_requests,
            "successful_requests": len(latencies),
            "failed_requests": errors,
            "error_rate_pct": round(error_rate, 2),
            "duration_sec": round(duration, 3),
            "throughput_rps": round(rps, 2),
            "mean_latency_ms": round(float(np.mean(arr)), 2),
            "p50_latency_ms": round(float(np.percentile(arr, 50)), 2),
            "p90_latency_ms": round(float(np.percentile(arr, 90)), 2),
            "p95_latency_ms": round(p95, 2),
            "p99_latency_ms": round(float(np.percentile(arr, 99)), 2),
            "p99_9_latency_ms": round(float(np.percentile(arr, 99.9)), 2),
            "is_sustainable": is_sustainable,
        }

    async def run_capacity_curve(
        self,
        concurrency_levels: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """Runs benchmarks across concurrency levels and identifies capacity points."""
        if concurrency_levels is None:
            concurrency_levels = [1, 5, 10, 25, 50, 100, 200]

        curve = []
        peak_rps = 0.0
        sustainable_rps = 0.0
        saturation_point = 100

        for c in concurrency_levels:
            total_reqs = max(c * 5, 50)
            res = await self.benchmark_concurrency_level(c, total_requests=total_reqs)
            curve.append(res)

            if res["throughput_rps"] > peak_rps:
                peak_rps = res["throughput_rps"]

            if res["is_sustainable"] and res["throughput_rps"] > sustainable_rps:
                sustainable_rps = res["throughput_rps"]
                saturation_point = c

        return {
            "peak_throughput_rps": round(peak_rps, 2),
            "sustainable_throughput_rps": round(sustainable_rps, 2),
            "optimal_concurrency_point": saturation_point,
            "curve_results": curve,
        }
