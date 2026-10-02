"""High-Throughput Concurrency & Load Runner for Phase 8.2.

Evaluates system throughput, latency percentiles, error rates, and memory
under concurrent workloads (1, 5, 10, 25, 50, 100 concurrency levels).
"""

import asyncio
import io
import os
import time
from typing import Dict, List, Any, Optional
import numpy as np
from PIL import Image

from app.document.pipeline import DocumentProcessingPipeline
from app.schemas.address import VerificationRequest
from app.verification.engine import VerificationEngine


class ConcurrencyRunner:
    """Runs concurrent load tests against the GeoVerify core engine."""

    def __init__(self):
        self.engine = VerificationEngine()
        self.doc_pipeline = DocumentProcessingPipeline(ocr_engine_name="mock")

    async def run_text_load(
        self,
        test_queries: List[str],
        concurrency: int = 10,
        total_requests: int = 100,
    ) -> Dict[str, Any]:
        """Runs concurrent text verification workload."""
        if not test_queries:
            test_queries = [
                "MG Road, Indiranagar, Bangalore, Karnataka 560038",
                "Shivaji Nagar, Pune, Maharashtra 411005",
                "Connaught Place, New Delhi, Delhi 110001",
                "Anna Salai, Chennai, Tamil Nadu 600002",
                "Park Street, Kolkata, West Bengal 700016",
            ]

        latencies: List[float] = []
        errors: int = 0
        semaphore = asyncio.Semaphore(concurrency)

        async def worker(query_idx: int):
            nonlocal errors
            query = test_queries[query_idx % len(test_queries)]
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
        total_duration = time.perf_counter() - t_start

        arr = np.array(latencies) if latencies else np.array([0.0])
        rps = total_requests / total_duration if total_duration > 0 else 0.0

        return {
            "workload": "text_verification",
            "concurrency": concurrency,
            "total_requests": total_requests,
            "successful_requests": len(latencies),
            "failed_requests": errors,
            "error_rate_pct": round((errors / total_requests) * 100.0, 2) if total_requests else 0.0,
            "total_duration_sec": round(total_duration, 3),
            "throughput_rps": round(rps, 2),
            "mean_latency_ms": round(float(np.mean(arr)), 2),
            "p50_latency_ms": round(float(np.percentile(arr, 50)), 2),
            "p90_latency_ms": round(float(np.percentile(arr, 90)), 2),
            "p95_latency_ms": round(float(np.percentile(arr, 95)), 2),
            "p99_latency_ms": round(float(np.percentile(arr, 99)), 2),
            "min_latency_ms": round(float(np.min(arr)), 2),
            "max_latency_ms": round(float(np.max(arr)), 2),
        }

    async def run_ocr_load(
        self,
        concurrency: int = 5,
        total_requests: int = 25,
    ) -> Dict[str, Any]:
        """Runs concurrent OCR document verification workload."""
        img = Image.new("RGB", (600, 400), color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        raw_bytes = buf.getvalue()

        latencies: List[float] = []
        errors: int = 0
        semaphore = asyncio.Semaphore(concurrency)

        async def worker():
            nonlocal errors
            async with semaphore:
                t0 = time.perf_counter()
                try:
                    res = await self.doc_pipeline.process_document(
                        file_bytes=raw_bytes,
                        filename="bench.png",
                        mime_type="image/png",
                        verify_geography=True,
                        engine_override="mock",
                    )
                    dt = (time.perf_counter() - t0) * 1000.0
                    latencies.append(dt)
                except Exception:
                    errors += 1

        t_start = time.perf_counter()
        tasks = [asyncio.create_task(worker()) for _ in range(total_requests)]
        await asyncio.gather(*tasks)
        total_duration = time.perf_counter() - t_start

        arr = np.array(latencies) if latencies else np.array([0.0])
        rps = total_requests / total_duration if total_duration > 0 else 0.0

        return {
            "workload": "ocr_document_verification",
            "concurrency": concurrency,
            "total_requests": total_requests,
            "successful_requests": len(latencies),
            "failed_requests": errors,
            "error_rate_pct": round((errors / total_requests) * 100.0, 2) if total_requests else 0.0,
            "total_duration_sec": round(total_duration, 3),
            "throughput_rps": round(rps, 2),
            "mean_latency_ms": round(float(np.mean(arr)), 2),
            "p50_latency_ms": round(float(np.percentile(arr, 50)), 2),
            "p90_latency_ms": round(float(np.percentile(arr, 90)), 2),
            "p95_latency_ms": round(float(np.percentile(arr, 95)), 2),
            "p99_latency_ms": round(float(np.percentile(arr, 99)), 2),
        }

    async def run_scaling_suite(
        self,
        test_queries: List[str],
        concurrency_levels: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        """Runs text load tests across 1, 5, 10, 25, 50, 100 concurrency levels."""
        if concurrency_levels is None:
            concurrency_levels = [1, 5, 10, 25, 50, 100]

        results = []
        for c in concurrency_levels:
            total_reqs = max(c * 5, 50)
            res = await self.run_text_load(
                test_queries=test_queries,
                concurrency=c,
                total_requests=total_reqs,
            )
            results.append(res)
        return results
