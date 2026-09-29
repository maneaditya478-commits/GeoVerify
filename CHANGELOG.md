# Changelog - GeoVerify India

All notable changes to the **GeoVerify India** platform are documented in this file.

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
