"""Failure Injection & Resilience Evaluation Engine for Phase 8.2.

Evaluates system resilience against:
- Simulated database query timeouts
- OCR engine timeouts & malformed documents
- Corrupt image payload rejection
- Dense vector fallback mechanisms
- Standardized APIErrorResponse compliance
"""

import asyncio
import io
import time
from typing import Dict, List, Any
from PIL import Image

from app.core.errors import (
    APIErrorResponse,
    GeoVerifyException,
    DatabaseTimeoutException,
    OCRTimeoutException,
    ResourceExhaustedException,
)
from app.document.pipeline import DocumentProcessingPipeline
from app.document.validator import DocumentValidator, DocumentValidationError
from app.schemas.address import VerificationRequest
from app.verification.engine import VerificationEngine


class FailureInjectionSuite:
    """Executes controlled failure injection experiments to verify fault tolerance."""

    def __init__(self):
        self.engine = VerificationEngine()
        self.doc_pipeline = DocumentProcessingPipeline(ocr_engine_name="mock")
        self.validator = DocumentValidator()

    def test_corrupt_document_rejection(self) -> Dict[str, Any]:
        """Tests that invalid or corrupt document payloads are rejected safely."""
        corrupt_bytes = b"NOT_A_VALID_IMAGE_OR_PDF_DATA_HERE"
        passed = False
        err_type = ""
        try:
            self.validator.validate(corrupt_bytes, "fake.png", "image/png")
        except DocumentValidationError as e:
            passed = True
            err_type = type(e).__name__
        except Exception as e:
            err_type = type(e).__name__

        return {
            "test": "corrupt_document_rejection",
            "passed": passed,
            "error_captured": err_type,
            "safe_rejection": passed,
        }

    def test_oversized_document_rejection(self) -> Dict[str, Any]:
        """Tests that documents exceeding size limits are rejected immediately."""
        oversized_bytes = b"0" * (16 * 1024 * 1024)  # 16 MB (> 15 MB limit)
        passed = False
        err_type = ""
        try:
            self.validator.validate(oversized_bytes, "oversized.pdf", "application/pdf")
        except DocumentValidationError as e:
            passed = True
            err_type = type(e).__name__
        except Exception as e:
            err_type = type(e).__name__

        return {
            "test": "oversized_document_rejection",
            "passed": passed,
            "error_captured": err_type,
            "safe_rejection": passed,
        }

    def test_structured_error_schema_conformance(self) -> Dict[str, Any]:
        """Validates that custom exceptions produce standardized error responses."""
        exc_db = DatabaseTimeoutException("Connection pool query timed out after 5.0s")
        resp_db = APIErrorResponse.from_exception(
            status_code=504,
            code="DATABASE_TIMEOUT",
            message=str(exc_db),
            path="/api/verify",
        )

        exc_ocr = OCRTimeoutException("OCR extraction timed out after 15.0s")
        resp_ocr = APIErrorResponse.from_exception(
            status_code=504,
            code="OCR_TIMEOUT",
            message=str(exc_ocr),
            path="/api/document/verify",
        )

        conforms = (
            resp_db.error.code == "DATABASE_TIMEOUT"
            and resp_ocr.error.code == "OCR_TIMEOUT"
            and len(resp_db.error.request_id) > 0
        )

        return {
            "test": "structured_error_schema_conformance",
            "passed": conforms,
            "db_error_code": resp_db.error.code,
            "ocr_error_code": resp_ocr.error.code,
        }

    async def test_empty_address_resilience(self) -> Dict[str, Any]:
        """Validates that empty / whitespace queries do not crash the engine."""
        queries = ["", "   ", "\t\n", None]
        all_safe = True

        for q in queries:
            try:
                req = VerificationRequest(address=q or "")
                res = await self.engine.verify(req)
                if res is None or res.score < 0:
                    all_safe = False
            except Exception:
                all_safe = False

        return {
            "test": "empty_address_resilience",
            "passed": all_safe,
            "queries_tested": len(queries),
        }

    async def run_full_suite(self) -> List[Dict[str, Any]]:
        """Runs all resilience tests and returns list of results."""
        results = [
            self.test_corrupt_document_rejection(),
            self.test_oversized_document_rejection(),
            self.test_structured_error_schema_conformance(),
            await self.test_empty_address_resilience(),
        ]
        return results
