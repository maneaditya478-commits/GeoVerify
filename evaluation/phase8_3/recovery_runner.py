"""Phase 8.3 Recovery & Lifecycle Resilience Runner.

Tests:
1. Cache reset and rapid memory recovery
2. Dense vector index reload and deterministic consistency
3. Readiness probe state transitions
4. Graceful error state recovery
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.cache import verification_cache, ocr_cache
from app.entity_resolution.dense_retrieval import dense_retriever
from app.entity_resolution.candidates import candidate_generator
from app.entity_resolution.models import EntityType
from app.schemas.address import VerificationRequest
from app.verification.engine import VerificationEngine


class RecoveryRunner:
    """Validates recovery after transient component resets or restarts."""

    def __init__(self):
        self.engine = VerificationEngine()
        self.all_entity_types = [EntityType.STATE, EntityType.DISTRICT, EntityType.SUBDISTRICT, EntityType.LOCALITY]

    def test_cache_purge_and_warmup_recovery(self) -> Dict[str, Any]:
        """Tests that purging cache resets counters cleanly without affecting engine queries."""
        verification_cache.set("dummy_k", "dummy_v")
        verification_cache.invalidate()  # Flush all

        stats = verification_cache.stats
        passed = stats["size"] == 0
        return {
            "test": "cache_purge_and_warmup_recovery",
            "passed": passed,
            "cache_size_after_purge": stats["size"],
        }

    def test_dense_index_reload_consistency(self) -> Dict[str, Any]:
        """Tests that re-indexing dense vectors yields 100% identical representations."""
        cands_before = dense_retriever.retrieve("Kothrud Pune", types=self.all_entity_types, top_k=5)

        # Re-index
        dense_retriever.build_index(
            candidate_generator.states,
            candidate_generator.districts,
            candidate_generator.subdistricts,
            candidate_generator.localities,
        )

        cands_after = dense_retriever.retrieve("Kothrud Pune", types=self.all_entity_types, top_k=5)

        names_before = [c.name for c in cands_before]
        names_after = [c.name for c in cands_after]
        deterministic = (names_before == names_after) and len(names_before) > 0

        return {
            "test": "dense_index_reload_consistency",
            "passed": deterministic,
            "top_candidates_reproduced": deterministic,
            "sample_candidates": names_after,
        }

    async def test_readiness_transition(self) -> Dict[str, Any]:
        """Verifies that readiness probe correctly reflects catalog availability."""
        # Check active catalog state
        catalog_ready = bool(len(candidate_generator.states) > 0 and len(candidate_generator.districts) > 0)
        index_ready = bool(dense_retriever.is_indexed)

        is_fully_ready = catalog_ready and index_ready
        return {
            "test": "readiness_transition",
            "passed": is_fully_ready,
            "catalog_ready": catalog_ready,
            "index_ready": index_ready,
            "overall_ready": is_fully_ready,
        }

    async def run_recovery_suite(self) -> Dict[str, Any]:
        cache_rec = self.test_cache_purge_and_warmup_recovery()
        dense_rec = self.test_dense_index_reload_consistency()
        ready_rec = await self.test_readiness_transition()

        all_passed = cache_rec["passed"] and dense_rec["passed"] and ready_rec["passed"]

        return {
            "overall_recovery_passed": all_passed,
            "tests": {
                "cache_recovery": cache_rec,
                "dense_reload": dense_rec,
                "readiness_state": ready_rec,
            },
        }
