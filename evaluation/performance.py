"""Component Micro-Benchmarking and Latency Profiler for GeoVerify India."""

import time
import asyncio
from typing import Dict, Any, List
import numpy as np
from app.services.normalizer import AddressNormalizer
from app.services.transliteration import transliteration_service
from app.services.address_parser import AddressParser
from app.entity_resolution.resolver import address_entity_resolver
from app.verification.engine import verification_engine
from app.schemas.address import VerificationRequest


class PerformanceProfiler:
    """Profiles execution latencies for individual pipeline components and end-to-end API workflows."""

    SAMPLE_ADDRESSES = [
        "Flat 402, Ganga Carnation, Near EON IT Park, Kharadi, Haveli, Pune, Maharashtra 411014",
        "गाव: खराडी, तालुका: हवेली, जिल्हा: पुणे, राज्य: महाराष्ट्र, पिन: 411014",
        "Whitefield, Bengaluru Urban, Karnataka 560066",
        "Near Metro Station, Connaught Place, New Delhi 110001",
        "Salt Lake, Sector 5, Kolkata, West Bengal 700091"
    ]

    @classmethod
    def _compute_stats(cls, latencies: List[float]) -> Dict[str, float]:
        if not latencies:
            return {}
        return {
            "mean_ms": round(float(np.mean(latencies)), 3),
            "median_ms": round(float(np.median(latencies)), 3),
            "p50_ms": round(float(np.percentile(latencies, 50)), 3),
            "p90_ms": round(float(np.percentile(latencies, 90)), 3),
            "p95_ms": round(float(np.percentile(latencies, 95)), 3),
            "p99_ms": round(float(np.percentile(latencies, 99)), 3),
            "min_ms": round(float(np.min(latencies)), 3),
            "max_ms": round(float(np.max(latencies)), 3)
        }

    @classmethod
    async def benchmark_components(cls, repetitions: int = 50) -> Dict[str, Any]:
        """Runs multi-repetition timing benchmarks across all core subsystems."""
        normalizer_latencies = []
        transliteration_latencies = []
        parser_latencies = []
        resolver_latencies = []
        verification_latencies = []

        # Warm-up
        for addr in cls.SAMPLE_ADDRESSES[:2]:
            AddressParser.parse(addr)
            await verification_engine.verify(VerificationRequest(address=addr))

        for _ in range(repetitions):
            for addr in cls.SAMPLE_ADDRESSES:
                # 1. Normalizer
                t0 = time.perf_counter()
                AddressNormalizer.normalize_address(addr)
                normalizer_latencies.append((time.perf_counter() - t0) * 1000)

                # 2. Transliteration & Script
                t0 = time.perf_counter()
                transliteration_service.detect_script(addr)
                transliteration_service.transliterate_to_latin(addr)
                transliteration_latencies.append((time.perf_counter() - t0) * 1000)

                # 3. Parser
                t0 = time.perf_counter()
                parsed = AddressParser.parse(addr)
                parser_latencies.append((time.perf_counter() - t0) * 1000)

                # 4. Entity Resolver
                t0 = time.perf_counter()
                address_entity_resolver.resolve_address(addr)
                resolver_latencies.append((time.perf_counter() - t0) * 1000)

                # 5. Full Verification Engine
                t0 = time.perf_counter()
                req = VerificationRequest(address=addr, include_geojson=False)
                await verification_engine.verify(req)
                verification_latencies.append((time.perf_counter() - t0) * 1000)

        return {
            "repetitions_per_sample": repetitions,
            "total_runs_per_component": repetitions * len(cls.SAMPLE_ADDRESSES),
            "components": {
                "address_normalizer": cls._compute_stats(normalizer_latencies),
                "indic_transliteration": cls._compute_stats(transliteration_latencies),
                "address_parser": cls._compute_stats(parser_latencies),
                "entity_resolution": cls._compute_stats(resolver_latencies),
                "verification_engine_pipeline": cls._compute_stats(verification_latencies)
            }
        }


def run_performance_profile():
    res = asyncio.run(PerformanceProfiler.benchmark_components(repetitions=40))
    print("\n================== GeoVerify India Component Latencies (ms) ==================")
    for comp, stats in res["components"].items():
        print(f"{comp:<30}: Mean={stats['mean_ms']:>6.3f}ms | P50={stats['p50_ms']:>6.3f}ms | P95={stats['p95_ms']:>6.3f}ms | P99={stats['p99_ms']:>6.3f}ms")
    print("=============================================================================\n")
    return res


if __name__ == "__main__":
    run_performance_profile()
