"""Retrieval Channel Ablation Evaluator (Phase 8).

Compares Recall@1, Recall@5, Recall@10 across individual retrieval channels:
- Exact Match Only
- Alias Match Only
- Transliteration Only
- Phonetic Only
- Length-Adaptive Fuzzy Only
- Admin Context Only
- PIN-Constrained Only
- Dense Geographic n-gram Only
- Spatial Proximity Only
- Full Multi-Stage Ensemble (All Channels)
Outputs CSV to evaluation/results/phase8/analysis/retrieval_channel_ablation.csv.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any

from app.entity_resolution.candidates import candidate_generator
from app.entity_resolution.ranking import ContextAwareRanker
from app.services.address_parser import AddressParser
from app.entity_resolution.models import EntityType


class RetrievalChannelAblationRunner:
    """Evaluates recall contribution of each retrieval channel."""

    def __init__(self):
        self.ranker = ContextAwareRanker()
        self.parser = AddressParser()

    def run_ablation(self, benchmark_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        channels = [
            "Exact_Only",
            "Alias_Only",
            "Transliteration_Only",
            "Phonetic_Only",
            "Fuzzy_Only",
            "Admin_Context_Only",
            "PIN_Constrained_Only",
            "Dense_Geographic_Only",
            "Spatial_Proximity_Only",
            "Full_Ensemble_All_Channels",
        ]

        results = []
        n = len(benchmark_cases)

        for ch in channels:
            r1_hits = 0
            r5_hits = 0
            r10_hits = 0

            for c in benchmark_cases:
                raw_text = c.get("raw_text", "")
                exp_loc = c.get("expected_locality")
                exp_dist = c.get("expected_district")
                exp_state = c.get("expected_state")
                exp_pin = c.get("expected_pincode")

                parsed = self.parser.parse(raw_text)
                query_tok = parsed.locality or parsed.district or parsed.city or raw_text

                # Retrieve candidates based on channel
                cands = self._retrieve_channel(ch, query_tok, exp_state, exp_dist, exp_pin)

                if not cands:
                    continue

                # Score candidates
                scored = []
                for cand in cands:
                    res = self.ranker.score_candidate(
                        candidate=cand,
                        query_text=query_tok,
                        context_state=exp_state or parsed.state,
                        context_district=exp_dist or parsed.district,
                        context_pin=exp_pin or parsed.pincode,
                    )
                    scored.append((res.match_score, cand))

                scored.sort(key=lambda x: x[0], reverse=True)

                # Check Recall@1
                if scored and self._is_hit(scored[0][1], exp_loc, exp_dist):
                    r1_hits += 1
                # Check Recall@5
                if any(self._is_hit(cand, exp_loc, exp_dist) for _, cand in scored[:5]):
                    r5_hits += 1
                # Check Recall@10
                if any(self._is_hit(cand, exp_loc, exp_dist) for _, cand in scored[:10]):
                    r10_hits += 1

            results.append({
                "channel_configuration": ch,
                "sample_count": n,
                "recall_at_1": round((r1_hits / n) * 100.0, 2) if n > 0 else 0.0,
                "recall_at_5": round((r5_hits / n) * 100.0, 2) if n > 0 else 0.0,
                "recall_at_10": round((r10_hits / n) * 100.0, 2) if n > 0 else 0.0,
            })

        return results

    def _is_hit(self, candidate, exp_loc: str, exp_dist: str) -> bool:
        if exp_loc and exp_loc.lower() in candidate.name.lower():
            return True
        if exp_dist and candidate.district and exp_dist.lower() in candidate.district.lower():
            return True
        return False

    def _retrieve_channel(
        self, channel_name: str, query_tok: str, exp_state: str, exp_dist: str, exp_pin: str
    ):
        types = [EntityType.LOCALITY, EntityType.DISTRICT, EntityType.STATE]

        if channel_name == "Exact_Only":
            return candidate_generator._retrieve_exact(query_tok.lower(), query_tok, types)
        elif channel_name == "Alias_Only":
            return candidate_generator._retrieve_aliases(query_tok.lower(), query_tok, types)
        elif channel_name == "Transliteration_Only":
            return candidate_generator._retrieve_transliteration(query_tok, query_tok.lower(), types)
        elif channel_name == "Phonetic_Only":
            return candidate_generator._retrieve_phonetic(query_tok.lower(), query_tok, types)
        elif channel_name == "Fuzzy_Only":
            return candidate_generator._retrieve_fuzzy(query_tok.lower(), types)
        elif channel_name == "Admin_Context_Only":
            return candidate_generator._retrieve_admin_context(query_tok.lower(), exp_state, exp_dist, None, types)
        elif channel_name == "PIN_Constrained_Only":
            return candidate_generator._retrieve_pin_constrained(exp_pin or "411038", query_tok.lower(), types)
        elif channel_name == "Dense_Geographic_Only":
            from app.entity_resolution.dense_retrieval import dense_retriever
            return dense_retriever.retrieve(query_tok, types, top_k=10)
        elif channel_name == "Spatial_Proximity_Only":
            from app.entity_resolution.spatial_retrieval import spatial_retriever
            from app.schemas.address import Coordinates
            return spatial_retriever.retrieve_nearby(Coordinates(latitude=18.5204, longitude=73.8567), types, radius_km=25.0)
        else:
            return candidate_generator.generate_candidates(
                token=query_tok,
                context_state=exp_state,
                context_district=exp_dist,
                context_pin=exp_pin,
                limit=10,
            )

    def save_csv(self, records: List[Dict[str, Any]], out_path: Path):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if not records:
            return
        fieldnames = list(records[0].keys())
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in records:
                writer.writerow(r)
