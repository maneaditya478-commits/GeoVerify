"""Detailed Field-Level Extraction Analysis for Phase 7.1.

Analyzes errors for:
1. District Extraction (Omission, Wrong State mapping, Alias failure, Preprocessing artifact)
2. Locality Extraction (Multi-token truncation, Premise confusion, Transliteration mismatch)
3. PIN Extraction (Digit substitution, Missing leading digit, Incomplete 6 digits)

Outputs structured CSV reports for error auditing.
"""

import csv
import io
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class DistrictErrorRecord(BaseModel):
    case_id: str
    category: str
    expected_district: str
    extracted_district: Optional[str]
    error_type: str  # OMISSION, ALIAS_FAILURE, MULTI_DISTRICT_CONFLICT, SCRIPT_MISMATCH
    remediation: str


class LocalityErrorRecord(BaseModel):
    case_id: str
    category: str
    expected_locality: str
    extracted_locality: Optional[str]
    error_type: str  # MULTI_TOKEN_TRUNCATION, PREMISE_CONFUSION, TRANSLITERATION_MISMATCH, OMISSION
    remediation: str


class PINErrorRecord(BaseModel):
    case_id: str
    category: str
    expected_pin: str
    extracted_pin: Optional[str]
    error_type: str  # DIGIT_SUBSTITUTION, MISSING_LEADING_DIGIT, OMISSION, WRONG_PIN
    remediation: str


class FieldAnalysisAuditor:
    """Audits field extractions and classifies error taxonomies."""

    @staticmethod
    def audit_district_error(
        case_id: str,
        category: str,
        expected: Optional[str],
        extracted: Optional[str],
        raw_text: str,
    ) -> Optional[DistrictErrorRecord]:
        if not expected or (extracted and expected.lower() in extracted.lower()):
            return None

        if not extracted:
            err_type = "OMISSION"
            remediation = "Apply PIN-first postal hierarchy lookup or subdistrict parent inference"
        elif " " in expected and expected.split()[0].lower() in extracted.lower():
            err_type = "PARTIAL_MATCH"
            remediation = "Normalize canonical district compound tokens"
        else:
            err_type = "DISTRICT_MISIDENTIFICATION"
            remediation = "Enhance administrative alias dictionary and boundary hierarchy resolution"

        return DistrictErrorRecord(
            case_id=case_id,
            category=category,
            expected_district=expected,
            extracted_district=extracted,
            error_type=err_type,
            remediation=remediation,
        )

    @staticmethod
    def audit_locality_error(
        case_id: str,
        category: str,
        expected: Optional[str],
        extracted: Optional[str],
        raw_text: str,
    ) -> Optional[LocalityErrorRecord]:
        if not expected or (extracted and (expected.lower() in extracted.lower() or extracted.lower() in expected.lower())):
            return None

        if not extracted:
            err_type = "OMISSION"
            remediation = "Add PIN-locality dictionary matching during segmentation"
        elif " " in expected and not (" " in extracted):
            err_type = "MULTI_TOKEN_TRUNCATION"
            remediation = "Support multi-token phrase matching across whitespace-separated tokens"
        else:
            err_type = "LOCALITY_MISIDENTIFICATION"
            remediation = "Refine premise vs locality indicator boundary rules"

        return LocalityErrorRecord(
            case_id=case_id,
            category=category,
            expected_locality=expected,
            extracted_locality=extracted,
            error_type=err_type,
            remediation=remediation,
        )

    @staticmethod
    def audit_pin_error(
        case_id: str,
        category: str,
        expected: Optional[str],
        extracted: Optional[str],
        raw_text: str,
    ) -> Optional[PINErrorRecord]:
        if not expected or extracted == expected:
            return None

        if not extracted:
            err_type = "OMISSION"
            remediation = "Run fuzzy regex scan with confusable digit substitution table"
        elif any(c.isalpha() for c in extracted):
            err_type = "DIGIT_SUBSTITUTION"
            remediation = "Repair confusable alphanumeric characters (O/0, l/1, S/5, B/8)"
        else:
            err_type = "WRONG_PIN"
            remediation = "Calibrate PIN candidate bounding box scoring"

        return PINErrorRecord(
            case_id=case_id,
            category=category,
            expected_pin=expected,
            extracted_pin=extracted,
            error_type=err_type,
            remediation=remediation,
        )

    @staticmethod
    def export_records_to_csv(records: List[BaseModel], file_path: str) -> None:
        """Export list of Pydantic error records to a CSV file."""
        if not records:
            # Write empty file with basic header
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                f.write("case_id,category,error_type,remediation\n")
            return

        fieldnames = list(records[0].model_dump().keys())
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in records:
                writer.writerow(r.model_dump())
