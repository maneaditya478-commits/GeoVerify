"""Phase 8.3 Cache Integrity, Security & Poisoning Resistance Auditor.

Validates:
1. Multi-state homonym cryptographic isolation (zero collision across states/districts)
2. Configuration & Data Version Invalidation safety
3. Strict Bounded LRU capacity limits & TTL expiration
4. High-contention concurrent access safety
5. Cache poisoning attack resistance
"""

import asyncio
import time
from typing import Dict, List, Any
from app.core.cache import (
    BoundedLRUTTLCache,
    CryptographicCacheKeyGenerator,
    verification_cache,
    ocr_cache,
)


class CacheSecurityAuditor:
    """Evaluates cryptographic safety and operational integrity of multi-tier caching."""

    def test_homonym_cryptographic_isolation(self) -> Dict[str, Any]:
        """Tests that identical names across multiple states/districts yield 100% unique keys."""
        homonym_entities = [
            {"query": "Rampur", "state": "Uttar Pradesh", "district": "Rampur", "pincode": "244901"},
            {"query": "Rampur", "state": "Bihar", "district": "Gaya", "pincode": "823001"},
            {"query": "Rampur", "state": "Himachal Pradesh", "district": "Shimla", "pincode": "172001"},
            {"query": "Bilaspur", "state": "Chhattisgarh", "district": "Bilaspur", "pincode": "495001"},
            {"query": "Bilaspur", "state": "Haryana", "district": "Yamunanagar", "pincode": "135102"},
            {"query": "Bilaspur", "state": "Himachal Pradesh", "district": "Bilaspur", "pincode": "174001"},
            {"query": "Aurangabad", "state": "Maharashtra", "district": "Chhatrapati Sambhaji Nagar", "pincode": "431001"},
            {"query": "Aurangabad", "state": "Bihar", "district": "Aurangabad", "pincode": "824101"},
        ]

        keys = set()
        details = []
        for ent in homonym_entities:
            k = CryptographicCacheKeyGenerator.generate_key(
                query=ent["query"],
                state=ent["state"],
                district=ent["district"],
                pincode=ent["pincode"],
            )
            keys.add(k)
            details.append({"entity": ent, "key": k})

        passed = len(keys) == len(homonym_entities)
        return {
            "test": "homonym_cryptographic_isolation",
            "total_homonyms": len(homonym_entities),
            "unique_keys_generated": len(keys),
            "zero_collision": passed,
            "details": details,
        }

    def test_version_invalidation_isolation(self) -> Dict[str, Any]:
        """Verifies that bumping config version or data version rotates all cache keys."""
        k_v82 = CryptographicCacheKeyGenerator.generate_key(
            query="Kothrud, Pune", config_version="8.2.0", data_version="1.0.0"
        )
        k_v83 = CryptographicCacheKeyGenerator.generate_key(
            query="Kothrud, Pune", config_version="8.3.0", data_version="1.0.0"
        )
        k_data_v2 = CryptographicCacheKeyGenerator.generate_key(
            query="Kothrud, Pune", config_version="8.3.0", data_version="2.0.0"
        )

        isolated = (k_v82 != k_v83) and (k_v83 != k_data_v2) and (k_v82 != k_data_v2)
        return {
            "test": "version_invalidation_isolation",
            "passed": isolated,
            "key_v8_2": k_v82,
            "key_v8_3": k_v83,
            "key_data_v2": k_data_v2,
        }

    def test_bounded_lru_and_ttl_behavior(self) -> Dict[str, Any]:
        """Verifies strict capacity enforcement and expiration."""
        cache = BoundedLRUTTLCache(maxsize=5, ttl_seconds=1)
        for i in range(12):
            cache.set(f"k_{i}", f"v_{i}")

        stats_immediate = cache.stats
        size_respected = stats_immediate["size"] == 5 and stats_immediate["evictions"] == 7

        # Test TTL expiration
        time.sleep(1.1)
        expired_val = cache.get("k_11")  # Should be expired
        stats_expired = cache.stats

        return {
            "test": "bounded_lru_and_ttl_behavior",
            "maxsize_configured": 5,
            "evictions_count": stats_immediate["evictions"],
            "size_respected": size_respected,
            "expired_entry_purged": expired_val is None,
            "passed": size_respected and (expired_val is None),
        }

    async def test_concurrent_cache_contention(self, concurrency: int = 25, operations: int = 500) -> Dict[str, Any]:
        """Verifies that high-concurrency writes/reads do not corrupt cache state."""
        cache = BoundedLRUTTLCache(maxsize=50, ttl_seconds=60)
        errors = 0

        async def worker(worker_id: int):
            nonlocal errors
            try:
                for i in range(operations // concurrency):
                    key = f"key_{i % 30}"
                    val = f"val_{worker_id}_{i}"
                    cache.set(key, val)
                    res = cache.get(key)
                    if res is None:
                        errors += 1
            except Exception:
                errors += 1

        tasks = [asyncio.create_task(worker(w)) for w in range(concurrency)]
        await asyncio.gather(*tasks)

        return {
            "test": "concurrent_cache_contention",
            "concurrency_tested": concurrency,
            "total_operations": operations,
            "errors_observed": errors,
            "passed": errors == 0 and cache.stats["size"] <= 50,
        }

    def test_cache_poisoning_resistance(self) -> Dict[str, Any]:
        """Verifies that malicious injection attempts in parameters cannot override canonical keys."""
        legit_key = CryptographicCacheKeyGenerator.generate_key(
            query="Pune", state="Maharashtra"
        )
        # Attempted injection with malicious delimiter manipulation
        injected_key = CryptographicCacheKeyGenerator.generate_key(
            query='Pune","st":"Maharashtra', state=""
        )

        passed = legit_key != injected_key
        return {
            "test": "cache_poisoning_resistance",
            "passed": passed,
            "legit_key": legit_key,
            "injected_key": injected_key,
        }

    async def run_full_audit(self) -> Dict[str, Any]:
        homonym = self.test_homonym_cryptographic_isolation()
        version = self.test_version_invalidation_isolation()
        lru_ttl = self.test_bounded_lru_and_ttl_behavior()
        concurrency = await self.test_concurrent_cache_contention()
        poisoning = self.test_cache_poisoning_resistance()

        all_passed = all([
            homonym["zero_collision"],
            version["passed"],
            lru_ttl["passed"],
            concurrency["passed"],
            poisoning["passed"],
        ])

        return {
            "overall_cache_integrity_passed": all_passed,
            "tests": {
                "homonym_isolation": homonym,
                "version_invalidation": version,
                "lru_ttl_eviction": lru_ttl,
                "concurrency_contention": concurrency,
                "poisoning_resistance": poisoning,
            },
        }
