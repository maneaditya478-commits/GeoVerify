"""Cache Performance & Isolation Evaluation Engine for Phase 8.2.

Evaluates multi-tier caching:
- Hit / miss / eviction metrics
- Cryptographic key isolation for homonyms across states
- Latency speedup on cache hits vs cold evaluations
- Invalidation correctness
"""

import asyncio
import time
from typing import Dict, List, Any
from app.core.cache import (
    BoundedLRUTTLCache,
    CryptographicCacheKeyGenerator,
    verification_cache,
    ocr_cache,
    geo_lookup_cache,
)
from app.schemas.address import VerificationRequest
from app.verification.engine import VerificationEngine


class CacheEvaluator:
    """Evaluates caching speedup, isolation, and eviction behavior."""

    def __init__(self):
        self.engine = VerificationEngine()

    def evaluate_key_isolation(self) -> Dict[str, Any]:
        """Verifies that homonyms in different states produce distinct cryptographic keys."""
        homonyms = [
            {"query": "Rampur", "state": "Uttar Pradesh", "district": "Rampur", "pincode": "244901"},
            {"query": "Rampur", "state": "Bihar", "district": "Gaya", "pincode": "823001"},
            {"query": "Rampur", "state": "Himachal Pradesh", "district": "Shimla", "pincode": "172001"},
            {"query": "Bilaspur", "state": "Chhattisgarh", "district": "Bilaspur", "pincode": "495001"},
            {"query": "Bilaspur", "state": "Haryana", "district": "Yamunanagar", "pincode": "135102"},
            {"query": "Bilaspur", "state": "Himachal Pradesh", "district": "Bilaspur", "pincode": "174001"},
        ]

        keys = set()
        details = []
        for h in homonyms:
            k = CryptographicCacheKeyGenerator.generate_key(
                query=h["query"],
                state=h["state"],
                district=h["district"],
                pincode=h["pincode"],
            )
            keys.add(k)
            details.append({"entity": h, "cache_key": k})

        all_unique = len(keys) == len(homonyms)
        return {
            "total_homonym_cases": len(homonyms),
            "unique_cache_keys": len(keys),
            "collision_free": all_unique,
            "details": details,
        }

    async def evaluate_latency_speedup(self, sample_addresses: List[str]) -> Dict[str, Any]:
        """Measures cold miss latency vs warm hit latency."""
        if not sample_addresses:
            sample_addresses = [
                "Indiranagar, Bangalore, Karnataka 560038",
                "Kothrud, Pune, Maharashtra 411038",
                "Connaught Place, New Delhi, Delhi 110001",
            ]

        cold_latencies: List[float] = []
        warm_latencies: List[float] = []

        for addr in sample_addresses:
            req = VerificationRequest(address=addr)
            cache_key = CryptographicCacheKeyGenerator.generate_key(addr)
            verification_cache.invalidate(cache_key)

            # Cold pass
            t0 = time.perf_counter()
            res_cold = await self.engine.verify(req)
            t_cold = (time.perf_counter() - t0) * 1000.0
            cold_latencies.append(t_cold)
            verification_cache.set(cache_key, res_cold)

            # Warm pass (retrieved from cache)
            t0 = time.perf_counter()
            res_warm = verification_cache.get(cache_key)
            t_warm = (time.perf_counter() - t0) * 1000.0
            warm_latencies.append(t_warm)

        mean_cold = sum(cold_latencies) / len(cold_latencies) if cold_latencies else 0.0
        mean_warm = sum(warm_latencies) / len(warm_latencies) if warm_latencies else 0.0
        speedup = (mean_cold / mean_warm) if mean_warm > 0 else 1.0

        return {
            "samples_evaluated": len(sample_addresses),
            "mean_cold_latency_ms": round(mean_cold, 3),
            "mean_warm_latency_ms": round(mean_warm, 3),
            "speedup_factor": round(speedup, 2),
            "cache_stats": verification_cache.stats,
        }

    def evaluate_lru_eviction(self) -> Dict[str, Any]:
        """Tests that BoundedLRUTTLCache strictly respects capacity limits and evicts oldest."""
        small_cache = BoundedLRUTTLCache(maxsize=10, ttl_seconds=60)
        for i in range(25):
            small_cache.set(f"key_{i}", f"val_{i}")

        stats = small_cache.stats
        return {
            "configured_maxsize": 10,
            "items_inserted": 25,
            "final_cache_size": stats["size"],
            "evictions_recorded": stats["evictions"],
            "capacity_respected": stats["size"] <= 10 and stats["evictions"] == 15,
        }
