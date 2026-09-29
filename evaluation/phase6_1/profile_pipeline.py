"""Comprehensive Performance Profiler for GeoVerify India Pipeline (Phase 6.1).

Micro-benchmarks every individual component of the verification and ranking pipeline:
- Normalization
- Parsing
- Candidate Generation
- Candidate Re-Ranking
- Hierarchy Validation
- Boundary Verification (Point-in-Polygon)
- PIN Code Validation
- Nearby Intelligence
- Ambiguity Detection
- Evidence Generation
- Evidence Graph Construction
- Decision Engine
- End-to-End Latency
"""

import sys
import time
import json
import asyncio
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from evaluation.load_dataset import DatasetLoader
from app.services.normalizer import AddressNormalizer
from app.services.address_parser import AddressParser
from app.services.geocoder import geocoder_service
from app.services.pin_validator import pin_validator
from app.services.nearby import nearby_service
from app.verification.hierarchy import hierarchy_validator
from app.verification.boundaries import boundary_service
from app.verification.evidence import EvidenceEngine
from app.verification.decision_engine import decision_engine
from app.entity_resolution.candidates import candidate_generator
from app.entity_resolution.ranking import context_aware_ranker
from app.entity_resolution.ambiguity import ambiguity_detector
from app.entity_resolution.models import EntityType
from app.evidence.graph import evidence_graph_builder
from app.schemas.address import VerificationRequest, Coordinates
from app.verification.engine import verification_engine


class PipelineProfiler:
    """Micro-benchmarks and generates component-by-component latency statistics."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (Path(__file__).parent.parent / "results" / "phase6_1")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def profile(self, repetitions: int = 50) -> Dict[str, Any]:
        print(f"\n================ Profiling GeoVerify India Pipeline ({repetitions} repetitions) ================")
        
        sample_addresses = [
            "Kharadi, Pune, Maharashtra 411014",
            "World Trade Center, Kharadi, Haveli, Pune, Maharashtra 411014",
            "Indiranagar, Bengaluru Urban, Karnataka 560038",
            "गाव: खराडी, तालुका: हवेली, जिल्हा: पुणे, महाराष्ट्र 411014",
            "Connaught Place, New Delhi, Delhi 110001",
            "Bandra West, Mumbai Suburban, Maharashtra 400050",
            "Salt Lake Sector V, Bidhannagar, North 24 Parganas, West Bengal 700091",
            "Banjara Hills, Hyderabad, Telangana 500034"
        ]

        timings: Dict[str, List[float]] = {
            "normalization": [],
            "parsing": [],
            "candidate_generation": [],
            "ranking": [],
            "hierarchy_validation": [],
            "boundary_pip": [],
            "pin_validation": [],
            "nearby_search": [],
            "ambiguity_detection": [],
            "evidence_generation": [],
            "evidence_graph": [],
            "decision_engine": [],
            "end_to_end": []
        }

        coords = Coordinates(latitude=18.5514, longitude=73.9405)

        for addr in sample_addresses:
            for _ in range(repetitions):
                # 1. Normalization
                t0 = time.perf_counter()
                norm = AddressNormalizer.normalize_address(addr)
                timings["normalization"].append((time.perf_counter() - t0) * 1000)

                # 2. Parsing
                t0 = time.perf_counter()
                parsed = AddressParser.parse(addr)
                timings["parsing"].append((time.perf_counter() - t0) * 1000)

                # 3. Candidate Generation
                t0 = time.perf_counter()
                loc_cands = candidate_generator.generate_candidates(
                    parsed.locality or "Kharadi",
                    expected_type=EntityType.LOCALITY,
                    context_state=parsed.state,
                    context_district=parsed.district,
                    limit=10
                )
                timings["candidate_generation"].append((time.perf_counter() - t0) * 1000)

                # 4. Ranking
                t0 = time.perf_counter()
                ranked = context_aware_ranker.rank_candidates(
                    candidates=loc_cands,
                    query_text=parsed.locality or "Kharadi",
                    context_state=parsed.state,
                    context_district=parsed.district,
                    expected_type=EntityType.LOCALITY
                )
                timings["ranking"].append((time.perf_counter() - t0) * 1000)

                # 5. Hierarchy Validation
                t0 = time.perf_counter()
                h_res = hierarchy_validator.validate_hierarchy(
                    state=parsed.state or "Maharashtra",
                    district=parsed.district or "Pune",
                    subdistrict=parsed.subdistrict,
                    locality=parsed.locality
                )
                timings["hierarchy_validation"].append((time.perf_counter() - t0) * 1000)

                # 6. Boundary PiP
                t0 = time.perf_counter()
                b_res = boundary_service.verify_boundaries(
                    coordinates=coords,
                    asserted_state=parsed.state or "Maharashtra",
                    asserted_district=parsed.district or "Pune"
                )
                timings["boundary_pip"].append((time.perf_counter() - t0) * 1000)

                # 7. PIN Validation
                t0 = time.perf_counter()
                pin_res = pin_validator.validate(
                    pincode=parsed.pincode or "411014",
                    state=parsed.state,
                    district=parsed.district,
                    coordinates=coords
                )
                timings["pin_validation"].append((time.perf_counter() - t0) * 1000)

                # 8. Nearby Search
                t0 = time.perf_counter()
                nearby_res = nearby_service.find_nearby(center=coords, radius_km=5.0)
                timings["nearby_search"].append((time.perf_counter() - t0) * 1000)

                # 9. Ambiguity Detection
                t0 = time.perf_counter()
                amb_res = ambiguity_detector.detect_ambiguity(ranked)
                timings["ambiguity_detection"].append((time.perf_counter() - t0) * 1000)

                # 10. Evidence Generation
                t0 = time.perf_counter()
                evid_items, expl, warns = EvidenceEngine.generate_evidence(
                    normalized=norm,
                    parsed=parsed,
                    geocoding=None,
                    hierarchy=h_res,
                    boundary=b_res,
                    pin=pin_res,
                    nearby=nearby_res.places
                )
                timings["evidence_generation"].append((time.perf_counter() - t0) * 1000)

                # 11. Evidence Graph Construction
                t0 = time.perf_counter()
                graph_obj = evidence_graph_builder.build_graph(
                    hierarchy=h_res,
                    boundary=b_res,
                    pin=pin_res,
                    coordinates=coords,
                    nearby_places=nearby_res.places,
                    evidence_items=evid_items
                )
                timings["evidence_graph"].append((time.perf_counter() - t0) * 1000)

                # 12. Decision Engine
                t0 = time.perf_counter()
                decision = decision_engine.evaluate(
                    consistency_score=90,
                    hierarchy=h_res,
                    boundary=b_res,
                    pin=pin_res,
                    is_ambiguous=amb_res.is_ambiguous
                )
                timings["decision_engine"].append((time.perf_counter() - t0) * 1000)

                # 13. Full End-to-End Pipeline
                t0 = time.perf_counter()
                await verification_engine.verify(VerificationRequest(address=addr, include_geojson=False))
                timings["end_to_end"].append((time.perf_counter() - t0) * 1000)

        # Compute summary statistics
        rows = []
        for comp, vals in timings.items():
            arr = np.array(vals)
            rows.append({
                "Component": comp,
                "Mean (ms)": round(float(np.mean(arr)), 3),
                "Std (ms)": round(float(np.std(arr)), 3),
                "P50 (ms)": round(float(np.percentile(arr, 50)), 3),
                "P95 (ms)": round(float(np.percentile(arr, 95)), 3),
                "P99 (ms)": round(float(np.percentile(arr, 99)), 3),
                "Min (ms)": round(float(np.min(arr)), 3),
                "Max (ms)": round(float(np.max(arr)), 3)
            })

        df = pd.DataFrame(rows)
        csv_path = self.output_dir / "phase6_1_latency_breakdown.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8")

        json_path = self.output_dir / "phase6_1_latency_breakdown.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)

        print("\nComponent Latency Profiling Results:")
        print(df.to_string(index=False))
        print(f"\n[OK] Latency profile exported to: {csv_path} and {json_path}")
        print("========================================================================\n")
        return {"components": rows}


def main():
    parser = argparse.ArgumentParser(description="Profile GeoVerify India Component Latency")
    parser.add_argument("--output", type=str, default="evaluation/results/phase6_1")
    parser.add_argument("--repetitions", type=int, default=30)
    args = parser.parse_args()

    profiler = PipelineProfiler(output_dir=Path(args.output))
    asyncio.run(profiler.profile(repetitions=args.repetitions))


if __name__ == "__main__":
    main()
