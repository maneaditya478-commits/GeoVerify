# Changelog - GeoVerify India

All notable changes to the **GeoVerify India** platform are documented in this file.

---

## [Phase 8.0] - 2026-09-30

### Multimodal Spatial Retrieval, Advanced Geographic Resolution & Multilingual OCR Recovery
- **Core Invariant Preserved**: GeoVerify verifies geographic consistency through deterministic evidence graphs and calibrated ranking, not opaque end-to-end classification.
- **Adaptive Image Preprocessing (`app.document.preprocessing.adaptive`)**:
  - Image quality profiler estimating DPI, skew angle, dynamic range, and blur.
  - Adaptive deskewing, Lanczos upscaling for low DPI scans, contrast enhancement, and unsharp mask sharpening.
- **Geographically Grounded Multilingual OCR Post-Correction (`app.document.address.post_corrector`)**:
  - Indic Devanagari numerals translation (`०-९` $\to$ `0-9`).
  - Devanagari-to-Romanized geographic alignment (e.g. `कोथरूड` $\to$ `Kothrud`, `पुणे` $\to$ `Pune`, `महाराष्ट्र` $\to$ `Maharashtra`).
  - Authority-anchored typo correction without ungrounded hallucinations.
- **Dense Geographic & Spatial Retrieval (`app.entity_resolution`)**:
  - `DenseGeographicRetriever`: Character n-gram vector representations and fast cosine similarity retrieval (`DENSE_GEOGRAPHIC`).
  - `SpatialProximityRetriever`: Coordinate distance (Haversine metric) and spatial neighborhood retrieval (`SPATIAL_PROXIMITY`).
  - Integrated into `MultiStageCandidateGenerator` behind `settings.ENABLE_DENSE_RETRIEVAL`.
- **Homonymous Locality Disambiguation**:
  - Disambiguates cross-jurisdictional duplicate place names (Rampur, Bilaspur, Shivaji Nagar, Gandhi Nagar) using parent administrative context.
  - Appropriately flags isolated homonym queries as `AMBIGUOUS` with explainable suggestions.
- **Key Empirical Results**:
  - **Recall@1**: Increased from 82.31% $\to$ **88.46%** (+6.15%).
  - **Locality Accuracy**: Increased from 84.23% $\to$ **91.54%** (+7.31%).
  - **Clean vs OCR Accuracy Gap**: Reduced from 10.00% down to **3.85%** (-6.15% gap closed).
  - **Macro F1**: Improved from 0.8460 $\to$ **0.9125**.
  - **246 / 246 tests passing** (184 backend + 62 evaluation).
  - Frontend production build verified.

---

## [Phase 7.3] - 2026-09-30

### Verification Decision Calibration & OCR-to-GeoVerify Handoff Gap Closure
- **Core Invariant**: Preserved strict distinction that GeoVerify verifies geographic consistency, not personal identity or fraud.
- **Missing vs Conflict Semantics**:
  - Implemented `EvidenceSemanticState` (`SUPPORTED`, `MISSING`, `CONFLICTING`, `UNKNOWN`) in `app.schemas.verification`.
  - Missing fields (uncoordinated spatial boundaries, omitted premises, missing subdistricts) are treated as incomplete/neutral rather than active contradictions.
- **Partial Address Handling**:
  - Geographically incomplete addresses (e.g. `Kharadi, Pune, Maharashtra 411014` or `Pune, Maharashtra`) verified as `CONSISTENT` or `VERIFIED` without structural completeness penalties.
- **Decision Engine Calibration**:
  - Calibrated decision score bands (`VERIFIED >= 80`, `CONSISTENT >= 60`, `NEEDS_REVIEW` calibrated).
  - Reduced `SAME_RESOLUTION_DIFFERENT_STATUS` cases from 16 to 12 (25% reduction).
  - Reduced Clean vs OCR status accuracy gap from 14.17% down to 10.00%.
- **Provenance & Evidence Strength**:
  - Validated weights across all 7 provenance channels (`EXPLICIT`, `OCR_REPAIRED`, `PIN_RECOVERY`, `ADMIN_CONTEXT_RECOVERY`, `FUZZY_MATCH`, `PHONETIC_MATCH`, `SPATIAL_MATCH`).
  - Eliminated unfair generic OCR penalties.
- **Diagnostics & Benchmarks**:
  - Added structured decision traces and complete diagnostic suite in `evaluation/phase7_3/`.
  - 228/228 unit and regression tests passing.
  - Mean latency reduced to 147.61 ms, P95 latency reduced to 167.32 ms.

---

## [Phase 7.2] - 2026-09-29

### OCR-to-GeoVerify Handoff Validation & Verification Regression Audit
- Evaluated 260 standardized cases under 60/20/20 split.
- Identified the 14.17% clean vs OCR handoff gap.
- Added pipeline tracing, earliest failure classifier, confusion matrix auditor, and latency profiler.

---

## [Phase 7.1] - 2026-09-29

### OCR Error Analysis & Multilingual Robustness
- Enhanced OCR normalizer for Indic numeral strings and character substitutions.
- Added PIN-first recovery and provenance tracking.

---

## [Phases 1 - 7.0]

- Initial MVP, Indian geographic data pipeline, entity resolution, ranking engine, and OCR document ingestion pipeline.
