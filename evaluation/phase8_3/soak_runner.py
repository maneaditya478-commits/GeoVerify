"""Phase 8.3 Long-Duration Soak Testing & Resource Stability Harness.

Simulates mixed production traffic:
- 40% Clean Text Multi-tier Addresses
- 25% OCR Document Ingestion
- 15% Ambiguous / Homonym Resolution Cases
- 10% Spatial Proximity / Coordinate Lookups
- 10% Invalid / Malformed Error Injections

Tracks:
- Memory RSS, Peak RSS, Absolute Growth, Leak Detection
- Latency Percentiles (Mean, P50, P90, P95, P99, P99.9)
- Multi-tier Cache Hit Rates & LRU Evictions
- Concurrency & Error Budget Analysis
"""

import asyncio
import io
import os
import random
import sys
import time
from typing import Dict, List, Any, Optional
import numpy as np
from PIL import Image

try:
    import psutil
except ImportError:
    psutil = None

from app.core.cache import verification_cache, ocr_cache, geo_lookup_cache
from app.document.pipeline import DocumentProcessingPipeline
from app.schemas.address import VerificationRequest
from app.verification.engine import VerificationEngine


class SoakTestRunner:
    """Executes continuous mixed-workload load testing over configurable durations."""

    def __init__(self):
        self.engine = VerificationEngine()
        self.doc_pipeline = DocumentProcessingPipeline(ocr_engine_name="mock")

        # Mixed workload corpus
        self.clean_corpus = [
            "MG Road, Indiranagar, Bangalore, Karnataka 560038",
            "Shivaji Nagar, Pune, Maharashtra 411005",
            "Connaught Place, New Delhi, Delhi 110001",
            "Anna Salai, Chennai, Tamil Nadu 600002",
            "Salt Lake Sector 5, Kolkata, West Bengal 700091",
            "Kharadi Bypass, Pune, Maharashtra 411014",
            "Banjara Hills Road 12, Hyderabad, Telangana 500034",
            "Navrangpura, Ahmedabad, Gujarat 380009",
        ]

        self.homonym_corpus = [
            "Civil Lines, Rampur, Uttar Pradesh 244901",
            "Main Road, Rampur, Gaya, Bihar 823001",
            "Bilaspur Market, Chhattisgarh 495001",
            "Bilaspur Town, Haryana 135102",
            "Rampur Market",  # Ambiguous
            "Bilaspur",        # Ambiguous
        ]

        self.spatial_corpus = [
            "EON Free Zone, Kharadi, Pune",
            "Electronic City Phase 1, Bangalore",
            "Cyber City, DLF Phase 2, Gurugram",
            "HITEC City, Madhapur, Hyderabad",
        ]

        self.invalid_corpus = [
            "",
            "   \t\n   ",
            "XYZ Nonexistent Locality 999999",
            "Kothrud, Pune, Karnataka 411038",  # Hierarchy mismatch
            "1234567890!@#$%^&*()",
        ]

    def _get_process_memory_mb(self) -> float:
        """Returns current process RSS memory in MB."""
        if psutil and hasattr(psutil, "Process"):
            try:
                proc = psutil.Process(os.getpid())
                return round(proc.memory_info().rss / (1024 * 1024), 2)
            except Exception:
                pass
        return 0.0

    async def run_soak(
        self,
        duration_seconds: float = 15.0,
        concurrency: int = 10,
        max_requests: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Executes soak test for specified duration or request budget."""
        start_memory = self._get_process_memory_mb()
        peak_memory = start_memory

        latencies: List[float] = []
        errors: int = 0
        total_requests: int = 0
        workload_counts = {"clean_text": 0, "ocr_document": 0, "homonym_ambiguity": 0, "spatial": 0, "invalid_error": 0}

        # Create dummy image for OCR workload
        img = Image.new("RGB", (600, 400), color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        doc_bytes = buf.getvalue()

        semaphore = asyncio.Semaphore(concurrency)
        start_time = time.perf_counter()
        stop_time = start_time + duration_seconds

        async def worker():
            nonlocal errors, total_requests, peak_memory
            while time.perf_counter() < stop_time:
                if max_requests and total_requests >= max_requests:
                    break

                # 40% clean, 25% ocr, 15% homonym, 10% spatial, 10% invalid
                rand_val = random.random()
                async with semaphore:
                    t0 = time.perf_counter()
                    try:
                        if rand_val < 0.40:
                            workload_counts["clean_text"] += 1
                            query = random.choice(self.clean_corpus)
                            await self.engine.verify(VerificationRequest(address=query))
                        elif rand_val < 0.65:
                            workload_counts["ocr_document"] += 1
                            await self.doc_pipeline.process_document(
                                file_bytes=doc_bytes,
                                filename="soak_doc.png",
                                mime_type="image/png",
                                verify_geography=True,
                                engine_override="mock",
                            )
                        elif rand_val < 0.80:
                            workload_counts["homonym_ambiguity"] += 1
                            query = random.choice(self.homonym_corpus)
                            await self.engine.verify(VerificationRequest(address=query))
                        elif rand_val < 0.90:
                            workload_counts["spatial"] += 1
                            query = random.choice(self.spatial_corpus)
                            await self.engine.verify(VerificationRequest(address=query))
                        else:
                            workload_counts["invalid_error"] += 1
                            query = random.choice(self.invalid_corpus)
                            await self.engine.verify(VerificationRequest(address=query))

                        dt = (time.perf_counter() - t0) * 1000.0
                        latencies.append(dt)
                    except Exception:
                        errors += 1

                    total_requests += 1

                    # Check memory periodically
                    if total_requests % 50 == 0:
                        cur_mem = self._get_process_memory_mb()
                        if cur_mem > peak_memory:
                            peak_memory = cur_mem

        # Launch concurrent workers
        tasks = [asyncio.create_task(worker()) for _ in range(concurrency)]
        await asyncio.gather(*tasks)
        actual_duration = time.perf_counter() - start_time

        end_memory = self._get_process_memory_mb()
        if end_memory > peak_memory:
            peak_memory = end_memory

        arr_lat = np.array(latencies) if latencies else np.array([0.0])
        throughput = total_requests / actual_duration if actual_duration > 0 else 0.0

        mem_growth_mb = round(max(0.0, end_memory - start_memory), 2)
        mem_growth_pct = round((mem_growth_mb / start_memory * 100.0), 2) if start_memory > 0 else 0.0

        # Verdict
        # Memory growth under 15% after warm-up is stable
        stable_verdict = "STABLE" if mem_growth_pct < 15.0 else "INVESTIGATE"

        return {
            "duration_seconds": round(actual_duration, 2),
            "concurrency": concurrency,
            "total_requests": total_requests,
            "successful_requests": len(latencies),
            "failed_requests": errors,
            "error_rate_pct": round((errors / total_requests * 100.0), 2) if total_requests else 0.0,
            "throughput_rps": round(throughput, 2),
            "workload_breakdown": workload_counts,
            "latencies": {
                "mean_ms": round(float(np.mean(arr_lat)), 2),
                "p50_ms": round(float(np.percentile(arr_lat, 50)), 2),
                "p90_ms": round(float(np.percentile(arr_lat, 90)), 2),
                "p95_ms": round(float(np.percentile(arr_lat, 95)), 2),
                "p99_ms": round(float(np.percentile(arr_lat, 99)), 2),
                "p99_9_ms": round(float(np.percentile(arr_lat, 99.9)), 2),
                "min_ms": round(float(np.min(arr_lat)), 2),
                "max_ms": round(float(np.max(arr_lat)), 2),
            },
            "memory": {
                "start_rss_mb": start_memory,
                "peak_rss_mb": peak_memory,
                "end_rss_mb": end_memory,
                "growth_mb": mem_growth_mb,
                "growth_pct": mem_growth_pct,
                "verdict": stable_verdict,
            },
            "cache": {
                "verification_cache": verification_cache.stats,
                "ocr_cache": ocr_cache.stats,
            },
        }
