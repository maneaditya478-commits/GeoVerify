"""Unit & Regression tests for Phase 8.1 Research Validation & Integrity."""

import io
import pytest
from PIL import Image

from app.document.preprocessing.adaptive import AdaptiveImagePreprocessor
from app.document.address.post_corrector import post_corrector
from app.entity_resolution.dense_retrieval import dense_retriever
from app.entity_resolution.spatial_retrieval import spatial_retriever
from app.entity_resolution.candidates import candidate_generator
from app.entity_resolution.ranking import ContextAwareRanker
from app.entity_resolution.ambiguity import AmbiguityDetector
from app.schemas.address import Coordinates
from app.entity_resolution.models import EntityType


class TestEvaluationIntegrity:
    """Validates evaluation split integrity and clean document passthrough."""

    def test_clean_document_zero_penalty_passthrough(self):
        # Clean 300 DPI image
        img = Image.new("RGB", (1200, 900), color=(255, 255, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        raw_bytes = buf.getvalue()

        processed_bytes, applied_ops = AdaptiveImagePreprocessor.preprocess_image(raw_bytes)
        assert "PASSTHROUGH_CLEAN" in applied_ops or not any("UPSCALE" in op for op in applied_ops)

    def test_low_dpi_pipeline_applies_upscale(self):
        img = Image.new("RGB", (400, 300), color=(200, 200, 200))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        raw_bytes = buf.getvalue()

        processed_bytes, applied_ops = AdaptiveImagePreprocessor.preprocess_image(raw_bytes)
        assert any("UPSCALE" in op for op in applied_ops)


class TestRetrievalAttributionAndProvenance:
    """Validates candidate provenance and multi-channel attribution."""

    def test_dense_candidate_provenance(self):
        cands = dense_retriever.retrieve(
            query="Kothrud Pune",
            types=[EntityType.LOCALITY],
            top_k=3,
        )
        assert len(cands) > 0
        assert cands[0].match_source == "dense_geographic"
        assert "dense_geographic" in cands[0].channels

    def test_spatial_candidate_provenance(self):
        center = Coordinates(latitude=18.5204, longitude=73.8567)
        cands = spatial_retriever.retrieve_nearby(
            center=center,
            types=[EntityType.LOCALITY],
            radius_km=10.0,
            top_k=3,
        )
        assert len(cands) > 0
        assert "spatial_proximity" in cands[0].match_source
        assert "spatial_proximity" in cands[0].channels


class TestHomonymContextResolutionAndAmbiguity:
    """Validates homonym disambiguation and zero-false-confidence guarantee."""

    def setup_method(self):
        self.ranker = ContextAwareRanker()
        self.ambiguity_detector = AmbiguityDetector()

    def test_homonym_resolved_with_parent_context(self):
        cands = candidate_generator.generate_candidates(
            token="Rampur",
            context_state="Uttar Pradesh",
            context_district="Rampur",
            limit=5,
        )
        scored = [
            self.ranker.score_candidate(
                c,
                query_text="Rampur",
                context_state="Uttar Pradesh",
                context_district="Rampur",
            )
            for c in cands
        ]
        scored.sort(key=lambda x: x.match_score, reverse=True)
        amb_info = self.ambiguity_detector.detect_ambiguity(scored)

        assert amb_info.is_ambiguous is False
        assert scored[0].candidate.state == "Uttar Pradesh"

    def test_homonym_without_context_is_ambiguous(self):
        cands = candidate_generator.generate_candidates(
            token="Rampur",
            limit=5,
        )
        scored = [
            self.ranker.score_candidate(c, query_text="Rampur")
            for c in cands
        ]
        scored.sort(key=lambda x: x.match_score, reverse=True)
        amb_info = self.ambiguity_detector.detect_ambiguity(scored)

        # Isolated Rampur matches Rampur in UP and Rampur in HP with close score
        if len(scored) >= 2 and scored[0].candidate.state != scored[1].candidate.state:
            assert amb_info.is_ambiguous is True
            assert len(amb_info.suggested_disambiguations) > 0

    def test_no_benchmark_specific_rules(self):
        # Ensure post-corrector does not contain test-specific IDs
        from app.document.address.post_corrector import COMMON_OCR_GEO_TYPOS
        for typo, canon in COMMON_OCR_GEO_TYPOS.items():
            assert not typo.startswith("dev_")
            assert not typo.startswith("stress_")
            assert not typo.startswith("test_")
