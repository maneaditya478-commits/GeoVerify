"""Multilingual Handoff & Degradation Analysis for Phase 7.2.

Stratifies Clean vs OCR handoff performance across:
- Language: English, Hindi, Marathi, Mixed
- Script: Latin, Devanagari, Mixed Script
- Evaluates OCR Degradation, Extraction Degradation, Entity Resolution Degradation, Status Degradation.
- Exports `evaluation/results/phase7_2/multilingual_handoff_analysis.csv`.
"""

import csv
from typing import Dict, Any, List
from collections import defaultdict
from pydantic import BaseModel


class MultilingualHandoffRow(BaseModel):
    stratum: str
    language: str
    script: str
    sample_count: int
    clean_locality_acc: float
    ocr_locality_acc: float
    locality_degradation: float
    clean_district_acc: float
    ocr_district_acc: float
    district_degradation: float
    clean_status_acc: float
    ocr_status_acc: float
    status_degradation: float
    entity_resolution_retention_pct: float


class MultilingualHandoffAnalyzer:
    """Computes language-stratified clean vs OCR handoff degradations."""

    @classmethod
    def evaluate_strata(cls, paired_results: List[Dict[str, Any]]) -> List[MultilingualHandoffRow]:
        grouped = defaultdict(list)
        for r in paired_results:
            key = f"{r.get('language', 'eng')}_{r.get('script', 'Latin')}"
            grouped[key].append(r)

        rows = []
        for key, items in grouped.items():
            tot = len(items)
            if tot == 0:
                continue
            lang, script = key.split("_", 1)

            c_loc = sum(1 for x in items if x.get("clean_locality_match", False)) / tot * 100.0
            o_loc = sum(1 for x in items if x.get("ocr_locality_match", False)) / tot * 100.0
            loc_deg = round(o_loc - c_loc, 2)

            c_dist = sum(1 for x in items if x.get("clean_district_match", False)) / tot * 100.0
            o_dist = sum(1 for x in items if x.get("ocr_district_match", False)) / tot * 100.0
            dist_deg = round(o_dist - c_dist, 2)

            c_stat = sum(1 for x in items if x.get("clean_status_match", False)) / tot * 100.0
            o_stat = sum(1 for x in items if x.get("ocr_status_match", False)) / tot * 100.0
            stat_deg = round(o_stat - c_stat, 2)

            same_res_count = sum(1 for x in items if x.get("ranking_classification") == "OCR_DID_NOT_CHANGE_RANKING")
            retention = round(same_res_count / tot * 100.0, 2)

            rows.append(MultilingualHandoffRow(
                stratum=key,
                language=lang,
                script=script,
                sample_count=tot,
                clean_locality_acc=round(c_loc, 2),
                ocr_locality_acc=round(o_loc, 2),
                locality_degradation=loc_deg,
                clean_district_acc=round(c_dist, 2),
                ocr_district_acc=round(o_dist, 2),
                district_degradation=dist_deg,
                clean_status_acc=round(c_stat, 2),
                ocr_status_acc=round(o_stat, 2),
                status_degradation=stat_deg,
                entity_resolution_retention_pct=retention,
            ))

        return rows

    @classmethod
    def export_csv(cls, rows: List[MultilingualHandoffRow], file_path: str):
        if not rows:
            return
        fieldnames = list(rows[0].model_dump().keys())
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in rows:
                writer.writerow(r.model_dump())
