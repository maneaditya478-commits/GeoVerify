"""Component Attribution & Recovery Cause Classifier for Phase 8.1.

Attribution Engine:
Analyzes cases where Phase 8 successfully recovers correct geographic entity or status
compared to Phase 7.3 baseline. Classifies primary and secondary recovery causes:
- OCR_RECOVERY
- NORMALIZATION_RECOVERY
- POST_CORRECTION_RECOVERY
- DENSE_RETRIEVAL_RECOVERY
- SPATIAL_RECOVERY
- RANKING_RECOVERY
- AMBIGUITY_RECOVERY
- INTERACTION_EFFECT
"""

import csv
from pathlib import Path
from typing import List, Dict, Any

from app.services.address_parser import AddressParser
from app.document.address.ocr_normalizer import OCRNormalizer
from app.document.address.post_corrector import post_corrector
from app.entity_resolution.candidates import candidate_generator
from app.entity_resolution.dense_retrieval import dense_retriever
from app.entity_resolution.spatial_retrieval import spatial_retriever
from app.entity_resolution.ranking import ContextAwareRanker
from app.entity_resolution.ambiguity import AmbiguityDetector
from app.entity_resolution.models import EntityType


class ComponentAttributionEngine:
    """Classifies which Phase 8 component contributed to each successful recovery."""

    def __init__(self):
        self.parser = AddressParser()
        self.ocr_normalizer = OCRNormalizer()
        self.post_corrector = post_corrector
        self.ranker = ContextAwareRanker()
        self.ambiguity_detector = AmbiguityDetector()

    def analyze_split(self, dataset_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        attribution_records = []

        for case in dataset_cases:
            case_id = case.get("id", "unknown")
            raw_text = case.get("raw_text", "")
            exp_state = case.get("expected_state")
            exp_dist = case.get("expected_district")
            exp_loc = case.get("expected_locality")
            exp_pin = case.get("expected_pincode")
            ground_truth_status = case.get("ground_truth_status", "VERIFIED")

            # 1. Baseline Evaluation (Phase 7.3 without Phase 8 features)
            base_norm = self.ocr_normalizer.normalize_text(raw_text)
            base_parsed = self.parser.parse(base_norm)
            base_tok = base_parsed.locality or base_parsed.district or base_parsed.city or raw_text

            base_cands = candidate_generator.generate_candidates(
                token=base_tok,
                context_state=exp_state or base_parsed.state,
                context_district=exp_dist or base_parsed.district,
                context_pin=exp_pin or base_parsed.pincode,
                limit=10,
            )
            # Remove Phase 8 dense/spatial channels for baseline simulation
            filtered_base_cands = [
                c for c in base_cands if c.match_source not in ["dense_geographic"] and "spatial_proximity" not in c.match_source
            ]
            base_scored = [
                self.ranker.score_candidate(
                    c,
                    query_text=base_tok,
                    context_state=exp_state or base_parsed.state,
                    context_district=exp_dist or base_parsed.district,
                    context_pin=exp_pin or base_parsed.pincode,
                )
                for c in filtered_base_cands
            ]
            base_scored.sort(key=lambda x: x.match_score, reverse=True)
            prev_rank = self._find_rank(base_scored, exp_loc, exp_dist)
            prev_status = "AMBIGUOUS" if self.ambiguity_detector.detect_ambiguity(base_scored).is_ambiguous else ("VERIFIED" if prev_rank == 1 else "NEEDS_REVIEW")

            # 2. Phase 8 Full Pipeline Evaluation
            # Post-correction
            post_norm, post_recs = self.post_corrector.post_correct(base_norm, context_state=exp_state)
            p8_parsed = self.parser.parse(post_norm)
            p8_tok = p8_parsed.locality or p8_parsed.district or p8_parsed.city or raw_text

            p8_cands = candidate_generator.generate_candidates(
                token=p8_tok,
                context_state=exp_state or p8_parsed.state,
                context_district=exp_dist or p8_parsed.district,
                context_pin=exp_pin or p8_parsed.pincode,
                limit=10,
            )
            p8_scored = [
                self.ranker.score_candidate(
                    c,
                    query_text=p8_tok,
                    context_state=exp_state or p8_parsed.state,
                    context_district=exp_dist or p8_parsed.district,
                    context_pin=exp_pin or p8_parsed.pincode,
                )
                for c in p8_cands
            ]
            p8_scored.sort(key=lambda x: x.match_score, reverse=True)
            final_rank = self._find_rank(p8_scored, exp_loc, exp_dist)
            amb_info = self.ambiguity_detector.detect_ambiguity(p8_scored)
            final_status = "AMBIGUOUS" if amb_info.is_ambiguous else ("VERIFIED" if final_rank == 1 else "NEEDS_REVIEW")

            # Determine which components helped
            adaptive_helped = bool(case.get("category") in ["dpi_degradation", "skew_degradation"])
            post_correction_helped = len(post_recs) > 0
            dense_helped = any(c.candidate.match_source == "dense_geographic" for c in p8_scored[:3])
            spatial_helped = any("spatial_proximity" in c.candidate.match_source for c in p8_scored[:3])
            ambiguity_helped = (ground_truth_status == "AMBIGUOUS" and final_status == "AMBIGUOUS")

            # Classify Primary Recovery Component
            if post_correction_helped and any(r["type"] == "DEVANAGARI_NUMERALS" for r in post_recs):
                primary_cause = "POST_CORRECTION_RECOVERY"
            elif post_correction_helped and any(r["type"] == "DEVANAGARI_GEO_TRANSLITERATION" for r in post_recs):
                primary_cause = "POST_CORRECTION_RECOVERY"
            elif dense_helped and (prev_rank != 1 and final_rank == 1):
                primary_cause = "DENSE_RETRIEVAL_RECOVERY"
            elif spatial_helped and (prev_rank != 1 and final_rank == 1):
                primary_cause = "SPATIAL_RECOVERY"
            elif ambiguity_helped:
                primary_cause = "AMBIGUITY_RECOVERY"
            elif adaptive_helped:
                primary_cause = "OCR_RECOVERY"
            elif prev_rank == final_rank and prev_status == final_status:
                primary_cause = "BASELINE_MAINTAINED"
            else:
                primary_cause = "INTERACTION_EFFECT"

            secondary = []
            if post_correction_helped and primary_cause != "POST_CORRECTION_RECOVERY":
                secondary.append("POST_CORRECTION")
            if dense_helped and primary_cause != "DENSE_RETRIEVAL_RECOVERY":
                secondary.append("DENSE_RETRIEVAL")
            if spatial_helped and primary_cause != "SPATIAL_RECOVERY":
                secondary.append("SPATIAL_PROXIMITY")

            attribution_records.append({
                "case_id": case_id,
                "raw_text": raw_text,
                "previous_rank": prev_rank if prev_rank != -1 else "NOT_FOUND",
                "final_rank": final_rank if final_rank != -1 else "NOT_FOUND",
                "previous_status": prev_status,
                "final_status": final_status,
                "ground_truth_status": ground_truth_status,
                "adaptive_preprocessing_helped": adaptive_helped,
                "post_correction_helped": post_correction_helped,
                "dense_retrieval_helped": dense_helped,
                "spatial_retrieval_helped": spatial_helped,
                "ambiguity_logic_helped": ambiguity_helped,
                "primary_recovery_component": primary_cause,
                "secondary_components": ";".join(secondary) if secondary else "NONE",
            })

        return attribution_records

    def _find_rank(self, scored_candidates: List[Any], exp_loc: str, exp_dist: str) -> int:
        for idx, res in enumerate(scored_candidates, start=1):
            c = res.candidate
            if exp_loc and exp_loc.lower() in c.name.lower():
                return idx
            if exp_dist and c.district and exp_dist.lower() in c.district.lower():
                return idx
        return -1

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
