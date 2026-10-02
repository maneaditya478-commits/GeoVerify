"""Latency Profiler & Breakdown Engine for Phase 8.2.

Profiles stage-by-stage latencies (P50, P90, P95, P99, Mean, Max) across:
- Normalization & Language Script Detection
- Character N-gram Vectorization & Dense Candidate Generation
- Hierarchical Spatial Verification & Ambiguity Resolution
- Context-Aware Ranking & Verification Decision Engine
- OCR Preprocessing & Address Extraction
"""

import asyncio
import io
import math
import numpy as np
import time
from typing import Dict, List, Any, Optional
from PIL import Image

from app.document.pipeline import DocumentProcessingPipeline
from app.entity_resolution.candidates import candidate_generator
from app.entity_resolution.dense_retrieval import dense_retriever
from app.entity_resolution.models import EntityType
from app.services.normalizer import AddressNormalizer
from app.schemas.address import VerificationRequest, StructuredAddressRequest
from app.verification.engine import VerificationEngine


class LatencyProfiler:
    """Profiles granular stage latencies of the GeoVerify processing pipeline."""

    def __init__(self):
        self.engine = VerificationEngine()
        self.doc_pipeline = DocumentProcessingPipeline(ocr_engine_name="mock")

    async def profile_address_pipeline(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Profiles the structured address verification pipeline stage-by-stage."""
        stage_timings: Dict[str, List[float]] = {
            "normalization": [],
            "candidate_generation": [],
            "dense_retrieval": [],
            "verification_decision": [],
            "total_end_to_end": [],
        }

        all_entity_types = [EntityType.STATE, EntityType.DISTRICT, EntityType.SUBDISTRICT, EntityType.LOCALITY]

        for case in test_cases:
            raw_address = case.get("raw_address") or case.get("raw_text") or case.get("raw") or case.get("query") or ""
            if not raw_address:
                continue

            t_total_0 = time.perf_counter()

            # 1. Normalization
            t0 = time.perf_counter()
            cleaned, _ = AddressNormalizer.clean_text(raw_address)
            tokens = [t.strip() for t in cleaned.split() if t.strip()]
            t_norm = (time.perf_counter() - t0) * 1000.0
            stage_timings["normalization"].append(t_norm)

            # 2. Candidate Generation (Rule/Catalog based)
            t0 = time.perf_counter()
            cands = candidate_generator.generate_candidates(cleaned)
            t_cand = (time.perf_counter() - t0) * 1000.0
            stage_timings["candidate_generation"].append(t_cand)

            # 3. Dense Retrieval
            t0 = time.perf_counter()
            dense_cands = dense_retriever.retrieve(
                raw_address,
                types=all_entity_types,
                top_k=10,
            ) if dense_retriever.is_indexed else []
            t_dense = (time.perf_counter() - t0) * 1000.0
            stage_timings["dense_retrieval"].append(t_dense)

            # 4. Full Verification Engine Execution
            req = VerificationRequest(address=raw_address)
            t0 = time.perf_counter()
            res = await self.engine.verify(req)
            t_ver = (time.perf_counter() - t0) * 1000.0
            stage_timings["verification_decision"].append(t_ver)

            t_total = (time.perf_counter() - t_total_0) * 1000.0
            stage_timings["total_end_to_end"].append(t_total)

        summary = {}
        for stage, times in stage_timings.items():
            if not times:
                continue
            arr = np.array(times)
            summary[stage] = {
                "count": len(times),
                "mean_ms": round(float(np.mean(arr)), 2),
                "p50_ms": round(float(np.percentile(arr, 50)), 2),
                "p90_ms": round(float(np.percentile(arr, 90)), 2),
                "p95_ms": round(float(np.percentile(arr, 95)), 2),
                "p99_ms": round(float(np.percentile(arr, 99)), 2),
                "min_ms": round(float(np.min(arr)), 2),
                "max_ms": round(float(np.max(arr)), 2),
            }

        return summary

    async def profile_document_pipeline(self, num_samples: int = 20) -> Dict[str, Any]:
        """Profiles the document OCR and address extraction pipeline."""
        img = Image.new("RGB", (600, 400), color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        raw_bytes = buf.getvalue()

        stage_timings: Dict[str, List[float]] = {
            "validation": [],
            "document_loading": [],
            "preprocessing": [],
            "ocr_execution": [],
            "region_detection": [],
            "field_extraction": [],
            "geographic_verification": [],
            "total_pipeline": [],
        }

        for _ in range(num_samples):
            res = await self.doc_pipeline.process_document(
                file_bytes=raw_bytes,
                filename="bench_doc.png",
                mime_type="image/png",
                verify_geography=True,
                engine_override="mock",
            )
            for k, v in res.stage_timings_ms.items():
                key = k.replace("_ms", "")
                if key in stage_timings:
                    stage_timings[key].append(v)
            if "total_pipeline_ms" in res.stage_timings_ms:
                stage_timings["total_pipeline"].append(res.stage_timings_ms["total_pipeline_ms"])

        summary = {}
        for stage, times in stage_timings.items():
            if not times:
                continue
            arr = np.array(times)
            summary[stage] = {
                "count": len(times),
                "mean_ms": round(float(np.mean(arr)), 2),
                "p50_ms": round(float(np.percentile(arr, 50)), 2),
                "p90_ms": round(float(np.percentile(arr, 90)), 2),
                "p95_ms": round(float(np.percentile(arr, 95)), 2),
                "p99_ms": round(float(np.percentile(arr, 99)), 2),
                "min_ms": round(float(np.min(arr)), 2),
                "max_ms": round(float(np.max(arr)), 2),
            }

        return summary
