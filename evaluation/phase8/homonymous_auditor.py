"""Homonymous Locality Disambiguation Auditor (Phase 8).

Audits system performance on cross-jurisdictional geographic homonyms
(e.g., Rampur, Bilaspur, Gandhi Nagar, Shivaji Nagar) under two conditions:
1. With Parent Administrative Context (District / State / PIN provided)
2. Without Parent Administrative Context (Isolated token, expected AMBIGUOUS)
Outputs CSV to evaluation/results/phase8/analysis/homonymous_locality_analysis.csv.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any

from app.entity_resolution.candidates import candidate_generator
from app.entity_resolution.ranking import ContextAwareRanker
from app.entity_resolution.ambiguity import AmbiguityDetector
from app.services.address_parser import AddressParser


class HomonymousLocalityAuditor:
    """Audits resolution of ambiguous place names."""

    def __init__(self):
        self.ranker = ContextAwareRanker()
        self.ambiguity_detector = AmbiguityDetector()
        self.parser = AddressParser()

    def audit_cases(self, homonym_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        records = []

        for case in homonym_cases:
            raw_text = case["raw_text"]
            exp_status = case["ground_truth_status"]
            exp_state = case.get("expected_state")
            exp_dist = case.get("expected_district")
            exp_loc = case.get("expected_locality")
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

            scored_matches = []
            for c in candidates:
                res = self.ranker.score_candidate(
                    candidate=c,
                    query_text=query_tok,
                    context_state=exp_state or parsed.state,
                    context_district=exp_dist or parsed.district,
                    context_pin=exp_pin or parsed.pincode,
                )
                scored_matches.append(res)

            scored_matches.sort(key=lambda x: x.match_score, reverse=True)

            ambiguity_info = self.ambiguity_detector.detect_ambiguity(scored_matches)
            predicted_status = "AMBIGUOUS" if ambiguity_info.is_ambiguous else "VERIFIED"

            is_correct = (predicted_status == exp_status)

            top1_c = scored_matches[0].candidate if scored_matches else None
            top2_c = scored_matches[1].candidate if len(scored_matches) > 1 else None

            records.append({
                "case_id": case.get("id", "homonym"),
                "query_text": raw_text,
                "token": query_tok,
                "context_provided": bool(exp_state or exp_dist or exp_pin),
                "expected_status": exp_status,
                "predicted_status": predicted_status,
                "is_correct": is_correct,
                "score_margin": ambiguity_info.score_margin,
                "top1_candidate": f"{top1_c.name} ({top1_c.district}, {top1_c.state})" if top1_c else "None",
                "top2_candidate": f"{top2_c.name} ({top2_c.district}, {top2_c.state})" if top2_c else "None",
                "disambiguation_suggestions": "; ".join(ambiguity_info.suggested_disambiguations),
            })

        return records

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
