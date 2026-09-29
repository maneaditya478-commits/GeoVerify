"""Diagnostic script to analyze candidate recall failures across the benchmark dataset."""

import json
from pathlib import Path
from rapidfuzz import fuzz
from evaluation.load_dataset import DatasetLoader
from app.services.address_parser import AddressParser
from app.services.transliteration import transliteration_service
from app.entity_resolution.candidates import candidate_generator
from app.entity_resolution.models import EntityType


def run_diagnostics():
    dataset_path = Path("evaluation/datasets/benchmark.json")
    dataset = DatasetLoader.load_from_json(dataset_path)

    diagnostics = {
        "total_cases": len(dataset.cases),
        "cases_with_locality_gt": 0,
        "recall_1_hits": 0,
        "recall_5_hits": 0,
        "recall_10_hits": 0,
        "failure_reasons": {
            "NO_EXACT_MATCH": 0,
            "NO_ALIAS_MATCH": 0,
            "NO_TRANSLITERATION_MATCH": 0,
            "NO_PHONETIC_MATCH": 0,
            "NO_FUZZY_MATCH": 0,
            "WRONG_ADMIN_CONTEXT": 0,
            "WRONG_ENTITY_TYPE": 0,
            "INSUFFICIENT_INDEX": 0,
            "PARSER_FAILURE": 0,
            "MISSING_DATA": 0,
            "UNKNOWN": 0
        },
        "detailed_failures": []
    }

    loc_names_in_catalog = set()
    for l in candidate_generator.localities:
        loc_names_in_catalog.add(l["name"].lower())
        if l.get("canonical_name"):
            loc_names_in_catalog.add(l["canonical_name"].lower())
        for a in l.get("aliases", []):
            loc_names_in_catalog.add(a.lower())

    for record in dataset.cases:
        gt = record.ground_truth
        if not gt.locality:
            continue
        diagnostics["cases_with_locality_gt"] += 1
        addr = record.address
        parsed = AddressParser.parse(addr)
        query_loc = parsed.locality or gt.locality

        # generate candidates as run_benchmark did
        cands = candidate_generator.generate_candidates(query_loc, expected_type=EntityType.LOCALITY, limit=10)
        cand_names = [c.name.lower() for c in cands]
        gt_loc = gt.locality.lower()

        hit_1 = len(cand_names) >= 1 and (gt_loc in cand_names[:1] or any(gt_loc in n or n in gt_loc for n in cand_names[:1]))
        hit_5 = len(cand_names) >= 1 and (gt_loc in cand_names[:5] or any(gt_loc in n or n in gt_loc for n in cand_names[:5]))
        hit_10 = len(cand_names) >= 1 and (gt_loc in cand_names[:10] or any(gt_loc in n or n in gt_loc for n in cand_names[:10]))

        if hit_1:
            diagnostics["recall_1_hits"] += 1
        if hit_5:
            diagnostics["recall_5_hits"] += 1
        if hit_10:
            diagnostics["recall_10_hits"] += 1

        if not hit_10:
            category = record.category.value
            script = record.script.value
            in_catalog = (gt_loc in loc_names_in_catalog or any(gt_loc in n for n in loc_names_in_catalog))

            if not in_catalog:
                reason = "INSUFFICIENT_INDEX"
            elif not parsed.locality and not parsed.unparsed_tokens:
                reason = "PARSER_FAILURE"
            elif script in ["DEVANAGARI", "MIXED"] or category in ["DEVANAGARI_HINDI", "DEVANAGARI_MARATHI", "MIXED_SCRIPT"]:
                reason = "NO_TRANSLITERATION_MATCH"
            elif category in ["HISTORICAL_NAME", "COLLOQUIAL_ALIAS"]:
                reason = "NO_ALIAS_MATCH"
            elif category in ["TYPO_MINOR", "TYPO_SEVERE"]:
                reason = "NO_FUZZY_MATCH"
            elif any(fuzz.ratio(query_loc.lower(), name) > 65 for name in loc_names_in_catalog):
                reason = "NO_PHONETIC_MATCH"
            elif category in ["MISSING_STATE", "MISSING_DISTRICT", "MISSING_PIN", "CORRECT_MINIMAL"]:
                reason = "MISSING_DATA"
            elif category in ["DISTRICT_MISMATCH", "SUBDISTRICT_MISMATCH"]:
                reason = "WRONG_ADMIN_CONTEXT"
            else:
                reason = "NO_EXACT_MATCH"

            diagnostics["failure_reasons"][reason] += 1
            diagnostics["detailed_failures"].append({
                "case_id": record.id,
                "address": record.address,
                "category": category,
                "ground_truth_locality": gt.locality,
                "parsed_locality": parsed.locality,
                "query_used": query_loc,
                "candidates_returned": cand_names,
                "failure_reason": reason
            })

    out_file = Path("evaluation/results/candidate_recall_diagnostics.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(diagnostics, f, indent=2, ensure_ascii=False)

    total_gt = diagnostics["cases_with_locality_gt"]
    print("================ CANDIDATE RECALL DIAGNOSTICS ================")
    print(f"Total Cases with Ground Truth Locality: {total_gt}")
    print(f"Recall@1  Hits : {diagnostics['recall_1_hits']} ({diagnostics['recall_1_hits'] / total_gt * 100:.2f}%)")
    print(f"Recall@5  Hits : {diagnostics['recall_5_hits']} ({diagnostics['recall_5_hits'] / total_gt * 100:.2f}%)")
    print(f"Recall@10 Hits : {diagnostics['recall_10_hits']} ({diagnostics['recall_10_hits'] / total_gt * 100:.2f}%)")
    print("\nRoot Cause Failure Breakdown:")
    for k, v in diagnostics["failure_reasons"].items():
        print(f"  {k:26s}: {v:4d} ({v / max(1, (total_gt - diagnostics['recall_10_hits'])) * 100:.1f}%)")
    print(f"Saved diagnostics to {out_file}")
    print("===============================================================")


if __name__ == "__main__":
    run_diagnostics()
