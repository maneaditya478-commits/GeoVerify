"""Clean Text vs OCR-Derived Address Control Experiment for Phase 7.2.

Isolates optical character recognition and document segmentation noise from
geographic verification, candidate ranking, and decision engine behavior.

Runs paired inputs:
- Input A (Clean): Ground truth structured/unstructured address text directly
- Input B (OCR): OCR-extracted document address candidate

Through the exact same GeoVerify VerificationEngine without configuration changes.
"""

import os
import sys
import csv
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.verification.engine import VerificationEngine
from app.schemas.address import VerificationRequest, StructuredAddressRequest
from app.schemas.verification import VerificationResponse
from app.document.pipeline import DocumentProcessingPipeline
from app.document.ocr.mock_engine import MockOCREngine
from evaluation.phase7_2.dataset import get_phase7_2_benchmark_cases, OCRTestCase, Split
from evaluation.phase7_2.helper import generate_synthetic_document_image

OUTPUT_DIR = ROOT_DIR / "evaluation" / "results" / "phase7_2"


class CleanVsOCRCaseResult(BaseModel):
    case_id: str
    category: str
    split: str
    ground_truth_address: str
    
    # Clean verification results
    clean_top_candidate: Optional[str]
    clean_score: float
    clean_status: str
    clean_ambiguous: bool
    clean_district_match: bool
    clean_locality_match: bool
    clean_status_match: bool
    
    # OCR verification results
    ocr_raw_text: str
    ocr_assembled_address: str
    ocr_top_candidate: Optional[str]
    ocr_score: float
    ocr_status: str
    ocr_ambiguous: bool
    ocr_district_match: bool
    ocr_locality_match: bool
    ocr_status_match: bool
    
    # Paired classification
    score_difference: float
    ranking_classification: str
    decision_classification: str


class CleanVsOCRRunner:
    """Executes paired clean-vs-OCR benchmark experiment."""

    def __init__(self):
        self.verif_engine = VerificationEngine()
        self.doc_pipeline = DocumentProcessingPipeline(ocr_engine_name="mock")

    async def evaluate_case(self, case: OCRTestCase) -> Optional[CleanVsOCRCaseResult]:
        gt = case.ground_truth
        if case.is_negative_case or not gt:
            return None

        # 1. Run Clean Verification (Input A)
        clean_req = VerificationRequest(
            address=gt.raw_text,
            structured=StructuredAddressRequest(
                address_line=gt.premise,
                locality=gt.locality,
                subdistrict=gt.subdistrict,
                district=gt.district,
                state=gt.state,
                pincode=gt.pincode,
            )
        )
        clean_verif: VerificationResponse = await self.verif_engine.verify(clean_req)
        clean_status_str = clean_verif.status.value if hasattr(clean_verif.status, "value") else str(clean_verif.status)
        clean_top_cand_obj = clean_verif.candidate_matches[0].candidate if (clean_verif.candidate_matches and len(clean_verif.candidate_matches) > 0) else None
        clean_top_cand = clean_top_cand_obj.name if clean_top_cand_obj else None
        clean_ambig = clean_verif.ambiguity.is_ambiguous if clean_verif.ambiguity else False

        clean_dist_match = bool(gt.district and clean_top_cand_obj and clean_top_cand_obj.district and gt.district.lower() in clean_top_cand_obj.district.lower())
        clean_loc_match = bool(gt.locality and clean_top_cand and gt.locality.lower() in clean_top_cand.lower())
        clean_stat_match = (clean_status_str == gt.expected_status) or (clean_status_str in ["VERIFIED", "CONSISTENT"] and gt.expected_status == "VERIFIED")

        # 2. Run OCR Pipeline (Input B)
        self.doc_pipeline.ocr_engine = MockOCREngine(predefined_text=case.document_text)
        img_bytes = generate_synthetic_document_image(case)
        doc_res = await self.doc_pipeline.process_document(
            file_bytes=img_bytes,
            filename=f"{case.case_id}.png",
            mime_type="image/png",
            verify_geography=True,
        )

        candidate = doc_res.primary_candidate
        ocr_verif: Optional[VerificationResponse] = getattr(candidate, "verification_result", None) or doc_res.verification
        ocr_status_str = "UNVERIFIED"
        ocr_score = 0.0
        ocr_top_cand = None
        ocr_top_cand_obj = None
        ocr_ambig = False

        if ocr_verif:
            ocr_status_str = ocr_verif.status.value if hasattr(ocr_verif.status, "value") else str(ocr_verif.status)
            ocr_score = ocr_verif.score
            ocr_top_cand_obj = ocr_verif.candidate_matches[0].candidate if (ocr_verif.candidate_matches and len(ocr_verif.candidate_matches) > 0) else None
            ocr_top_cand = ocr_top_cand_obj.name if ocr_top_cand_obj else None
            ocr_ambig = ocr_verif.ambiguity.is_ambiguous if ocr_verif.ambiguity else False

        ocr_dist_match = bool(gt.district and ocr_top_cand_obj and ocr_top_cand_obj.district and gt.district.lower() in ocr_top_cand_obj.district.lower())
        ocr_loc_match = bool(gt.locality and ocr_top_cand and gt.locality.lower() in ocr_top_cand.lower())
        ocr_stat_match = (ocr_status_str == gt.expected_status) or (ocr_status_str in ["VERIFIED", "CONSISTENT"] and gt.expected_status == "VERIFIED")

        # Classifications
        score_diff = round(ocr_score - clean_verif.score, 2)
        if clean_top_cand == ocr_top_cand:
            rank_cls = "OCR_DID_NOT_CHANGE_RANKING"
        elif not ocr_top_cand and clean_top_cand:
            rank_cls = "OCR_DESTROYED_CANDIDATE_RECALL"
        elif ocr_loc_match and not clean_loc_match:
            rank_cls = "OCR_IMPROVED_RANKING"
        else:
            rank_cls = "OCR_CAUSED_RANKING_CHANGE"

        if clean_top_cand == ocr_top_cand:
            if clean_status_str == ocr_status_str:
                dec_cls = "IDENTICAL_DECISION"
            else:
                dec_cls = "SAME_RESOLUTION_DIFFERENT_STATUS"
        else:
            dec_cls = "DIFFERENT_RESOLUTION_DIFFERENT_STATUS"

        return CleanVsOCRCaseResult(
            case_id=case.case_id,
            category=case.category,
            split=case.split.value,
            ground_truth_address=gt.raw_text,
            clean_top_candidate=clean_top_cand,
            clean_score=clean_verif.score,
            clean_status=clean_status_str,
            clean_ambiguous=clean_ambig,
            clean_district_match=clean_dist_match,
            clean_locality_match=clean_loc_match,
            clean_status_match=clean_stat_match,
            ocr_raw_text=case.document_text,
            ocr_assembled_address=candidate.assembled_address if candidate else "",
            ocr_top_candidate=ocr_top_cand,
            ocr_score=ocr_score,
            ocr_status=ocr_status_str,
            ocr_ambiguous=ocr_ambig,
            ocr_district_match=ocr_dist_match,
            ocr_locality_match=ocr_loc_match,
            ocr_status_match=ocr_stat_match,
            score_difference=score_diff,
            ranking_classification=rank_cls,
            decision_classification=dec_cls,
        )

    async def run_all(self, cases: List[OCRTestCase]) -> List[CleanVsOCRCaseResult]:
        results = []
        for c in cases:
            res = await self.evaluate_case(c)
            if res:
                results.append(res)
        return results

    @staticmethod
    def export_csv(results: List[CleanVsOCRCaseResult], file_path: Path):
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if not results:
            return
        fieldnames = list(results[0].model_dump().keys())
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r.model_dump())

    @staticmethod
    def export_markdown(results: List[CleanVsOCRCaseResult], file_path: Path):
        total = len(results)
        if total == 0:
            return

        clean_status_acc = sum(1 for r in results if r.clean_status_match) / total * 100.0
        ocr_status_acc = sum(1 for r in results if r.ocr_status_match) / total * 100.0

        clean_dist_acc = sum(1 for r in results if r.clean_district_match) / total * 100.0
        ocr_dist_acc = sum(1 for r in results if r.ocr_district_match) / total * 100.0

        clean_loc_acc = sum(1 for r in results if r.clean_locality_match) / total * 100.0
        ocr_loc_acc = sum(1 for r in results if r.ocr_locality_match) / total * 100.0

        same_res_diff_stat = sum(1 for r in results if r.decision_classification == "SAME_RESOLUTION_DIFFERENT_STATUS")
        ocr_no_rank_change = sum(1 for r in results if r.ranking_classification == "OCR_DID_NOT_CHANGE_RANKING")

        md = []
        md.append("# Clean Text vs OCR Address Verification Control Experiment (Phase 7.2)\n")
        md.append("## 1. Summary Comparison\n")
        md.append("| Metric | Clean Ground-Truth Input | OCR-Derived Input | Delta | Retention |")
        md.append("| :--- | :---: | :---: | :---: | :---: |")
        md.append(f"| **Locality Match Rate** | {clean_loc_acc:.2f}% | {ocr_loc_acc:.2f}% | {ocr_loc_acc - clean_loc_acc:+.2f}% | {ocr_loc_acc/clean_loc_acc*100:.1f}% |")
        md.append(f"| **District Match Rate** | {clean_dist_acc:.2f}% | {ocr_dist_acc:.2f}% | {ocr_dist_acc - clean_dist_acc:+.2f}% | {ocr_dist_acc/clean_dist_acc*100:.1f}% |")
        md.append(f"| **Status Accuracy** | {clean_status_acc:.2f}% | {ocr_status_acc:.2f}% | {ocr_status_acc - clean_status_acc:+.2f}% | {ocr_status_acc/clean_status_acc*100:.1f}% |\n")

        md.append("## 2. Paired Behavioral Classifications\n")
        md.append(f"- **Total Evaluated Address Pairs**: {total}")
        md.append(f"- **OCR Did Not Change Ranking**: {ocr_no_rank_change} ({ocr_no_rank_change/total*100:.1f}%)")
        md.append(f"- **Same Resolution, Different Status (Decision Discrepancy)**: {same_res_diff_stat} ({same_res_diff_stat/total*100:.1f}%)\n")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md))
