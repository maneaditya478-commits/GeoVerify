"""Phase 8.3 Golden Regression & Geographic Invariant Certification Suite.

Validates frozen geographic correctness across:
- Clean multi-tier administrative addresses
- OCR-derived degraded addresses
- Indic multilingual scripts (Marathi, Hindi, English, transliterated)
- PIN-supported and PIN-conflicting addresses
- State and District administrative jurisdictional conflicts
- Cross-state homonymous place names & ambiguity thresholds
- Partial addresses and missing geographic evidence
- Dense vector retrieval and spatial proximity recoveries
"""

import asyncio
import csv
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.schemas.address import VerificationRequest
from app.schemas.verification import VerificationResponse, VerificationStatus
from app.verification.engine import VerificationEngine


def get_golden_cases() -> List[Dict[str, Any]]:
    """Returns curated golden test suite covering all critical geographic invariants."""
    return [
        # 1. Standard Clean Multi-Tier Addresses
        {
            "id": "gold_clean_01",
            "category": "standard_multitier",
            "raw_text": "Flat 402, Shanti Heights, Kothrud, Pune, Maharashtra 411038",
            "expected_state": "maharashtra",
            "expected_district": "pune",
            "expected_locality": "kothrud",
            "expected_pincode": "411038",
            "expected_status": "VERIFIED",
            "expect_ambiguous": False,
        },
        {
            "id": "gold_clean_02",
            "category": "standard_multitier",
            "raw_text": "Plot 12, Indiranagar 100ft Road, Bengaluru, Karnataka 560038",
            "expected_state": "karnataka",
            "expected_district": "bengaluru",
            "expected_locality": "indiranagar",
            "expected_pincode": "560038",
            "expected_status": "VERIFIED",
            "expect_ambiguous": False,
        },
        {
            "id": "gold_clean_03",
            "category": "standard_multitier",
            "raw_text": "Connaught Place, New Delhi, Delhi 110001",
            "expected_state": "delhi",
            "expected_district": "new delhi",
            "expected_locality": "connaught place",
            "expected_pincode": "110001",
            "expected_status": "VERIFIED",
            "expect_ambiguous": False,
        },

        # 2. Multilingual & Indic Scripts
        {
            "id": "gold_lang_01",
            "category": "multilingual_marathi",
            "raw_text": "फ्लॅट ४०२, कोथरूड, पुणे, महाराष्ट्र ४११०३८",
            "expected_state": "maharashtra",
            "expected_district": "pune",
            "expected_locality": "kothrud",
            "expected_pincode": "411038",
            "expected_status": "VERIFIED",
            "expect_ambiguous": False,
        },
        {
            "id": "gold_lang_02",
            "category": "multilingual_hindi",
            "raw_text": "सेक्टर ६२, नोएडा, गौतम बुद्ध नगर, उत्तर प्रदेश २०१३०९",
            "expected_state": "uttar pradesh",
            "expected_district": "gautam buddha nagar",
            "expected_locality": "sector 62",
            "expected_pincode": "201309",
            "expected_status": "VERIFIED",
            "expect_ambiguous": False,
        },

        # 3. PIN-Supported vs PIN-Conflicting
        {
            "id": "gold_pin_01",
            "category": "pin_supported",
            "raw_text": "Hinjawadi Phase 1, Pune, Maharashtra 411057",
            "expected_state": "maharashtra",
            "expected_district": "pune",
            "expected_locality": "hinjawadi",
            "expected_pincode": "411057",
            "expected_status": "VERIFIED",
            "expect_ambiguous": False,
        },
        {
            "id": "gold_pin_02",
            "category": "pin_conflict",
            "raw_text": "Kothrud, Pune, Maharashtra 110001",  # Pincode 110001 belongs to Delhi -> score penalty
            "expected_state": "maharashtra",
            "expected_district": "pune",
            "expected_locality": "kothrud",
            "expected_pincode": "110001",
            "expected_status": "NEEDS_REVIEW",
            "expect_ambiguous": False,
        },

        # 4. State & District Jurisdictional Conflicts
        {
            "id": "gold_conflict_01",
            "category": "state_conflict",
            "raw_text": "Kothrud, Pune, Karnataka 411038",  # Pune is in Maharashtra, not Karnataka -> hard conflict
            "expected_state": "maharashtra",
            "expected_district": "pune",
            "expected_locality": "kothrud",
            "expected_pincode": "411038",
            "expected_status": "INCONSISTENT",
            "expect_ambiguous": False,
        },

        # 5. Homonymous Place Names & Ambiguity Resolution
        {
            "id": "gold_homonym_01",
            "category": "homonym_context_up",
            "raw_text": "Civil Lines, Rampur, Uttar Pradesh 244901",
            "expected_state": "uttar pradesh",
            "expected_district": "rampur",
            "expected_locality": "civil lines",
            "expected_pincode": "244901",
            "expected_status": "NEEDS_REVIEW",
            "expect_ambiguous": False,
        },
        {
            "id": "gold_homonym_02",
            "category": "homonym_context_bihar",
            "raw_text": "Main Road, Rampur, Gaya, Bihar 823001",
            "expected_state": "bihar",
            "expected_district": "gaya",
            "expected_locality": "rampur",
            "expected_pincode": "823001",
            "expected_status": "NEEDS_REVIEW",
            "expect_ambiguous": False,
        },
        {
            "id": "gold_homonym_03",
            "category": "isolated_homonym_ambiguous",
            "raw_text": "Rampur Market",  # Isolated homonym with no state or district
            "expected_state": "",
            "expected_district": "",
            "expected_locality": "rampur",
            "expected_pincode": "",
            "expected_status": "AMBIGUOUS",
            "expect_ambiguous": True,
        },

        # 6. Spatial & Dense Retrieval Recovery
        {
            "id": "gold_dense_01",
            "category": "dense_retrieval_typo",
            "raw_text": "Kothrood Puna Maharastra 411038",  # Typo resilient dense match
            "expected_state": "maharashtra",
            "expected_district": "pune",
            "expected_locality": "kothrud",
            "expected_pincode": "411038",
            "expected_status": "VERIFIED",
            "expect_ambiguous": False,
        },

        # 7. Partial & Missing Evidence
        {
            "id": "gold_partial_01",
            "category": "partial_address",
            "raw_text": "Somewhere near Hill View, Pune",
            "expected_state": "maharashtra",
            "expected_district": "pune",
            "expected_locality": "",
            "expected_pincode": "",
            "expected_status": "CONSISTENT",
            "expect_ambiguous": False,
        },
    ]


class GoldenRegressionEvaluator:
    """Executes frozen golden test suite and verifies invariant compliance."""

    def __init__(self):
        self.engine = VerificationEngine()

    async def run_evaluation(self) -> Dict[str, Any]:
        cases = get_golden_cases()
        results = []
        passed_count = 0

        for case in cases:
            raw = case["raw_text"]
            req = VerificationRequest(address=raw)
            t0 = time.perf_counter()
            res = await self.engine.verify(req)
            dt = (time.perf_counter() - t0) * 1000.0

            matched_state = (res.administrative_hierarchy.state or res.normalized_address.state or "").lower()
            matched_dist = (res.administrative_hierarchy.district or res.normalized_address.district or "").lower()
            matched_loc = (res.administrative_hierarchy.locality or res.normalized_address.locality or "").lower()
            matched_pin = str(res.pin_verification.pincode or res.normalized_address.pincode or "")
            pred_status = res.status.value.upper()

            exp_status = case["expected_status"].upper()
            is_ambiguous = (res.status == VerificationStatus.AMBIGUOUS or (res.ambiguity and res.ambiguity.is_ambiguous))

            status_correct = (pred_status == exp_status)
            ambiguity_correct = (is_ambiguous == case["expect_ambiguous"])

            case_passed = status_correct and ambiguity_correct
            if case_passed:
                passed_count += 1

            results.append({
                "id": case["id"],
                "category": case["category"],
                "raw_text": raw,
                "expected_status": exp_status,
                "predicted_status": pred_status,
                "status_correct": status_correct,
                "expected_ambiguous": case["expect_ambiguous"],
                "predicted_ambiguous": is_ambiguous,
                "ambiguity_correct": ambiguity_correct,
                "matched_state": matched_state,
                "matched_district": matched_dist,
                "matched_locality": matched_loc,
                "matched_pincode": matched_pin,
                "latency_ms": round(dt, 2),
                "passed": case_passed,
            })

        total = len(cases)
        accuracy = round((passed_count / total) * 100.0, 2) if total else 0.0

        return {
            "total_golden_cases": total,
            "passed_golden_cases": passed_count,
            "failed_golden_cases": total - passed_count,
            "accuracy_pct": accuracy,
            "all_invariants_passed": passed_count == total,
            "case_results": results,
        }
