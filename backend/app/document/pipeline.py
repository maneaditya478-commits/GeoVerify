"""Document verification pipeline orchestration module (Phase 7).

Orchestrates:
1. Document Validation & Security checks (MIME, magic bytes, dimensions, size, pages)
2. Document Page Extraction & Decoding
3. Image Preprocessing (grayscale, contrast, denoising, deskew, thresholding)
4. Quality Evaluation (sharpness, contrast, blur, brightness)
5. Multi-language OCR execution (Tesseract / Mock engine with bounding boxes)
6. Address Region Isolation (header-anchored & spatial clustering)
7. Structured Field Extraction & OCR normalization
8. PIN-First administrative & locality recovery
9. Verification-Engine invocation (GeoVerify core authority)
"""

import time
import uuid
import io
from typing import Optional, List, Dict, Any, Tuple
from PIL import Image

from app.document.validator import DocumentValidator
from app.document.loader import DocumentLoader
from app.document.image_preprocessor import ImagePreprocessor
from app.document.quality import DocumentQualityEvaluator
from app.document.ocr import get_ocr_engine
from app.document.ocr.language_detection import detect_language_scripts
from app.document.address.region_detector import AddressRegionDetector
from app.document.address.assembler import AddressCandidateAssembler
from app.document.models import (
    DocumentType,
    OCRResult,
    OCRPage,
    OCRQualityStatus,
    AddressExtractionStatus,
    ExtractedAddressCandidate,
)
from app.schemas.document import (
    DocumentMetadata,
    OCRMetadata,
    AddressExtractionMetadata,
    DocumentVerificationResponse,
)
from app.schemas.address import VerificationRequest, StructuredAddressRequest
from app.verification.engine import VerificationEngine


class DocumentProcessingPipeline:
    """End-to-end document OCR and geographic verification orchestrator."""

    def __init__(self, ocr_engine_name: str = "auto"):
        self.validator = DocumentValidator()
        self.loader = DocumentLoader()
        self.preprocessor = ImagePreprocessor()
        self.quality_evaluator = DocumentQualityEvaluator()
        self.ocr_engine = get_ocr_engine(ocr_engine_name)
        self.region_detector = AddressRegionDetector()
        self.candidate_assembler = AddressCandidateAssembler()
        self.verification_engine = VerificationEngine()

    async def process_document(
        self,
        file_bytes: bytes,
        filename: str,
        mime_type: Optional[str] = None,
        verify_geography: bool = True,
        engine_override: Optional[str] = None,
    ) -> DocumentVerificationResponse:
        """Run complete document ingestion, OCR, address extraction, and verification pipeline."""
        timings: Dict[str, float] = {}
        transformation_pipeline: List[Dict[str, Any]] = []

        # Stage 1: Validation
        t0 = time.perf_counter()
        validation_res = self.validator.validate(file_bytes, filename, mime_type)
        t_val = (time.perf_counter() - t0) * 1000.0
        timings["validation_ms"] = round(t_val, 2)
        
        transformation_pipeline.append({
            "stage": "validation",
            "status": "passed",
            "detected_type": validation_res.detected_type.value,
            "size_bytes": validation_res.size_bytes,
            "sha256": validation_res.sha256[:12] + "...",
        })

        doc_meta = DocumentMetadata(
            document_id=f"doc_{uuid.uuid4().hex[:12]}",
            filename=validation_res.sanitized_filename,
            file_type=validation_res.detected_type,
            mime_type=validation_res.mime_type,
            size_bytes=validation_res.size_bytes,
            page_count=0,
            sha256=validation_res.sha256,
        )

        # Stage 2: Page Loading & Conversion
        t0 = time.perf_counter()
        raw_images = self.loader.load_pages(file_bytes, validation_res.detected_type)
        doc_meta.page_count = len(raw_images)
        t_load = (time.perf_counter() - t0) * 1000.0
        timings["document_loading_ms"] = round(t_load, 2)

        transformation_pipeline.append({
            "stage": "document_loading",
            "page_count": len(raw_images),
            "dimensions": [{"width": img.width, "height": img.height} for img in raw_images],
        })

        # Select OCR Engine
        engine = get_ocr_engine(engine_override) if engine_override else self.ocr_engine

        # Stage 3: Image Preprocessing, Quality Assessment & OCR per page
        ocr_pages: List[OCRPage] = []
        preprocessed_images: List[Image.Image] = []
        quality_evaluations = []

        t_prep_total = 0.0
        t_ocr_total = 0.0

        for page_idx, page_item in enumerate(raw_images, start=1):
            img = page_item.image if hasattr(page_item, "image") else page_item
            # Preprocessing
            t_p0 = time.perf_counter()
            prep_res = self.preprocessor.preprocess(img)
            prep_img = prep_res.image
            deskew_angle = prep_res.rotation_deg
            t_prep_total += (time.perf_counter() - t_p0) * 1000.0
            preprocessed_images.append(prep_img)

            # Quality Assessment
            quality_report = self.quality_evaluator.evaluate(img)
            quality_evaluations.append(quality_report)

            # OCR Execution
            t_o0 = time.perf_counter()
            ocr_page = engine.process_page(prep_img, page_num=page_idx)
            t_ocr_total += (time.perf_counter() - t_o0) * 1000.0
            ocr_pages.append(ocr_page)

        timings["preprocessing_ms"] = round(t_prep_total, 2)
        timings["ocr_execution_ms"] = round(t_ocr_total, 2)

        # Merge OCR Results across pages
        full_text = "\n\n".join(p.text for p in ocr_pages).strip()
        mean_conf = sum(p.confidence for p in ocr_pages) / len(ocr_pages) if ocr_pages else 0.0
        
        # Overall quality status is min of pages
        overall_quality = quality_evaluations[0].quality_status if quality_evaluations else OCRQualityStatus.HIGH
        
        # Detected languages across all text
        detected_langs = detect_language_scripts(full_text)
        primary_lang = max(detected_langs.items(), key=lambda x: x[1])[0] if detected_langs else "eng"

        ocr_res = OCRResult(
            document_id=doc_meta.document_id,
            engine=engine.engine_name,
            pages=ocr_pages,
            full_text=full_text,
            mean_confidence=round(mean_conf, 2),
            primary_language=primary_lang,
            quality_status=overall_quality,
            processing_time_ms=round(t_ocr_total, 2),
        )

        ocr_meta = OCRMetadata(
            status="SUCCESS" if full_text else "FAILED",
            engine=engine.engine_name,
            mean_confidence=round(mean_conf, 2),
            quality_status=overall_quality,
            primary_language=primary_lang,
            languages_detected=detected_langs,
            pages_processed=len(ocr_pages),
            processing_time_ms=round(t_ocr_total, 2),
            ocr_result=ocr_res,
        )

        transformation_pipeline.append({
            "stage": "ocr_extraction",
            "engine": engine.engine_name,
            "mean_confidence": round(mean_conf, 2),
            "primary_language": primary_lang,
            "total_words_extracted": sum(len(p.words) for p in ocr_pages),
            "quality_status": overall_quality.value,
        })

        # Stage 4: Address Region Detection
        t0 = time.perf_counter()
        regions = self.region_detector.detect_regions(ocr_res)
        t_reg = (time.perf_counter() - t0) * 1000.0
        timings["region_detection_ms"] = round(t_reg, 2)

        transformation_pipeline.append({
            "stage": "address_region_detection",
            "regions_found": len(regions),
            "regions": [
                {
                    "region_id": r.region_id,
                    "address_type": r.address_type.value,
                    "confidence": r.confidence,
                    "has_header": bool(r.header_keyword_detected),
                }
                for r in regions
            ],
        })

        # Stage 5: Structured Field Extraction & PIN Recovery
        t0 = time.perf_counter()
        candidates = self.candidate_assembler.assemble_candidates(regions)
        t_ext = (time.perf_counter() - t0) * 1000.0
        timings["field_extraction_ms"] = round(t_ext, 2)

        primary_candidate = candidates[0] if candidates else None
        has_pin_rec = any(c.pin_recovered for c in candidates)

        addr_ext_meta = AddressExtractionMetadata(
            status=primary_candidate.extraction_status if primary_candidate else AddressExtractionStatus.FAILED,
            extraction_confidence=primary_candidate.extraction_confidence if primary_candidate else 0.0,
            total_candidates_found=len(candidates),
            selected_candidate_index=0 if candidates else -1,
            extracted_fields_count=len(primary_candidate.fields) if primary_candidate else 0,
            pin_recovered=has_pin_rec,
            processing_time_ms=round(t_ext, 2),
        )

        transformation_pipeline.append({
            "stage": "address_field_extraction",
            "total_candidates": len(candidates),
            "primary_extracted_fields": list(primary_candidate.fields.keys()) if primary_candidate else [],
            "pin_recovered": has_pin_rec,
            "assembled_address": primary_candidate.assembled_address if primary_candidate else None,
        })

        # Stage 6: Geographic Verification (if requested and candidate exists)
        verification_response = None
        if verify_geography and primary_candidate and primary_candidate.assembled_address:
            t0 = time.perf_counter()
            
            # Map structured components to verification request
            struct = primary_candidate.structured_components
            req = VerificationRequest(
                address=primary_candidate.assembled_address,
                structured=StructuredAddressRequest(
                    address_line=struct.get("street") or struct.get("premise"),
                    locality=struct.get("locality"),
                    subdistrict=struct.get("subdistrict"),
                    district=struct.get("district"),
                    state=struct.get("state"),
                    pincode=struct.get("pincode"),
                ) if any(struct.values()) else None
            )

            verification_response = await self.verification_engine.verify(req)
            primary_candidate.verification_result = verification_response
            t_ver = (time.perf_counter() - t0) * 1000.0
            timings["geographic_verification_ms"] = round(t_ver, 2)

            transformation_pipeline.append({
                "stage": "geographic_verification",
                "status": verification_response.status.value,
                "score": verification_response.score,
                "entity_match_score": verification_response.scores.entity_match if verification_response.scores else None,
                "pincode_matched": verification_response.pin_verification.matched if verification_response.pin_verification else None,
            })

        # Summary generation
        summary_lines = []
        if primary_candidate:
            summary_lines.append(f"Extracted {len(primary_candidate.fields)} address fields ({primary_candidate.extraction_status.value})")
            if has_pin_rec:
                summary_lines.append("PIN-first recovery applied to correct noisy locality tokens.")
            if verification_response:
                summary_lines.append(f"Geographic verification status: {verification_response.status.value} (Score: {verification_response.score}/100)")
        else:
            summary_lines.append("No structured address candidate could be isolated from document text.")

        total_time = sum(timings.values())
        timings["total_pipeline_ms"] = round(total_time, 2)

        return DocumentVerificationResponse(
            document=doc_meta,
            ocr=ocr_meta,
            address_extraction=addr_ext_meta,
            address_candidates=candidates,
            primary_candidate=primary_candidate,
            verification=verification_response,
            transformation_pipeline=transformation_pipeline,
            stage_timings_ms=timings,
            summary=" | ".join(summary_lines),
        )
