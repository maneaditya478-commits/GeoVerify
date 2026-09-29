"""Top-1 Failure Taxonomy and Diagnostics for Phase 8.1.

Analyzes instances where Recall@5 is SUCCESS but Recall@1 is FAILURE.
Deterministically classifies the underlying failure mechanism.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any

from app.services.address_parser import AddressParser
from app.entity_resolution.candidates import candidate_generator
from app.entity_resolution.ranking import ContextAwareRanker


class Top1TaxonomyAnalyzer:
    """Taxonomy classifier for Recall@1 failures."""

    def __init__(self):
        self.parser = AddressParser()
        self.ranker = ContextAwareRanker()

    def analyze_split(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        failures = []

        for case in cases:
            case_id = case.get("id", "case")
            raw_text = case.get("raw_text", "")
            exp_loc = case.get("expected_locality")
            exp_dist = case.get("expected_district")
            exp_state = case.get("expected_state")
            exp_pin = case.get("expected_pincode")

            parsed = self.parser.parse(raw_text)
            query_tok = parsed.locality or parsed.district or parsed.city or exp_loc or raw_text

            candidates = candidate_generator.generate_candidates(
                token=query_tok,
                context_state=exp_state or parsed.state,
                context_district=exp_dist or parsed.district,
                context_pin=exp_pin or parsed.pincode,
                limit=10,
            )

            scored = []
            for c in candidates:
                res = self.ranker.score_candidate(
                    candidate=c,
                    query_text=query_tok,
                    context_state=exp_state or parsed.state,
                    context_district=exp_dist or parsed.district,
                    context_pin=exp_pin or parsed.pincode,
                )
                scored.append((res.match_score, c, res))

            scored.sort(key=lambda x: x[0], reverse=True)
            if not scored:
                continue

            # Check if Rank 1 matches target
            top1_cand = scored[0][1]
            top1_matches = self._is_hit(top1_cand, exp_loc, exp_dist)

            if not top1_matches:
                # Check if target is present in Top 5
                target_rank = -1
                for rank_idx, (score, cand, res) in enumerate(scored[:5], start=1):
                    if self._is_hit(cand, exp_loc, exp_dist):
                        target_rank = rank_idx
                        break

                if target_rank > 1:
                    top_score, top_entity, top_res = scored[0]
                    target_score, target_entity, target_res = scored[target_rank - 1]
                    score_diff = round(top_score - target_score, 2)

                    category = self._classify_error(top_res, target_res, raw_text, exp_loc, exp_dist, exp_state, exp_pin)

                    failures.append({
                        "case_id": case_id,
                        "raw_text": raw_text,
                        "correct_entity": target_entity.name,
                        "correct_rank": target_rank,
                        "top_entity": top_entity.name,
                        "top_score": top_score,
                        "correct_score": target_score,
                        "score_difference": score_diff,
                        "name_similarity_top": top_res.breakdown.name_similarity,
                        "name_similarity_correct": target_res.breakdown.name_similarity,
                        "admin_context_top": top_res.breakdown.admin_context,
                        "admin_context_correct": target_res.breakdown.admin_context,
                        "pin_score_top": top_res.breakdown.pin_compatibility,
                        "pin_score_correct": target_res.breakdown.pin_compatibility,
                        "spatial_score_top": top_res.breakdown.geographic_proximity,
                        "spatial_score_correct": target_res.breakdown.geographic_proximity,
                        "retrieval_channels_top": ";".join(top_entity.channels or [top_entity.match_source]),
                        "retrieval_channels_correct": ";".join(target_entity.channels or [target_entity.match_source]),
                        "error_category": category,
                    })

        return failures

    def _is_hit(self, cand, exp_loc: str, exp_dist: str) -> bool:
        if exp_loc and exp_loc.lower() in cand.name.lower():
            return True
        if exp_dist and cand.district and exp_dist.lower() in cand.district.lower():
            return True
        return False

    def _classify_error(self, top_res, target_res, raw_text, exp_loc, exp_dist, exp_state, exp_pin) -> str:
        if not exp_state and not exp_dist and not exp_pin:
            return "MISSING_CONTEXT"
        if top_res.candidate.name.lower() == target_res.candidate.name.lower():
            return "HOMONYM_ERROR"
        if top_res.breakdown.name_similarity > target_res.breakdown.name_similarity + 5.0:
            return "NAME_SIMILARITY_ERROR"
        if top_res.breakdown.admin_context > target_res.breakdown.admin_context:
            return "ADMIN_CONTEXT_ERROR"
        if top_res.breakdown.pin_compatibility > target_res.breakdown.pin_compatibility:
            return "PIN_ERROR"
        if top_res.candidate.entity_type != target_res.candidate.entity_type:
            return "ENTITY_TYPE_ERROR"
        return "RANKING_WEIGHT_ERROR"

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
