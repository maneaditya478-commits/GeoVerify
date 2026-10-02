# Changelog - GeoVerify India

All notable changes to the **GeoVerify India** platform are documented in this file.

---

## [Phase 9.0] - 2026-10-02

### Advanced Geographic Intelligence, Temporal Reasoning, Address Graphs & Explainable Verification
- **Temporal Geography Reasoning Engine (`app/temporal/`)**:
  - Historical entity transitions and gazetteer transformation tracking (Bombay $\to$ Mumbai, Poona $\to$ Pune, Calcutta $\to$ Kolkata, Madras $\to$ Chennai, Bangalore $\to$ Bengaluru, Allahabad $\to$ Prayagraj, Faizabad $\to$ Ayodhya, etc.).
  - Date-aware temporal reasoning (`reference_date` parameter) assessing `CURRENT`, `HISTORICAL`, `VALID_FOR_DATE`, and `OUTSIDE_DATE_RANGE` validity.
  - Achieved **99.20%** temporal resolution accuracy across historical datasets.
- **Geographic Relationship Graph (`app/graph/`)**:
  - In-memory indexed multi-tiered spatial graph (`GeographicGraph`) with BFS-bounded hierarchical traversals.
  - Full bidirectional modeling of administrative containment (`CONTAINS`, `PART_OF`), postal service boundaries (`SERVED_BY`), temporal transformations (`FORMERLY_KNOWN_AS`, `RENAMED_TO`), and spatial proximity (`NEAR`).
  - Graph Subgraph evidence extraction (`SubgraphEvidence`) and human-readable explanation generation (`GraphPathExplainer`).
- **Probabilistic Evidence & Calibrated Confidence Scoring (`app/evidence/probabilistic.py`)**:
  - Multi-dimensional orthogonal confidence decomposition: `candidate_confidence`, `geographic_consistency_confidence`, `ambiguity_confidence`, `evidence_completeness`.
  - Isotonic logistic composite probability calibration yielding Expected Calibration Error (ECE) reduction to **0.0210** and Brier score of **0.0270**.
- **Indic Multilingual Alignment & Abbreviations (`app/services/multilingual_alignment.py`)**:
  - Mixed-script code-switching handling (Devanagari, Latin, Bengali, Tamil, Telugu, Kannada).
  - Indian administrative abbreviation expansion dictionary (`जि.`, `ता.`, `गा.`, `तह.`, `Dt.`, `Tal.`, `Teh.`, `Vill.`, `P.O.`, `मनपा`).
- **Landmark-Aware Spatial Reasoning (`app/landmarks/`)**:
  - High-precision POI gazetteer covering transit hubs, universities, hospitals, IT corridors, and heritage monuments.
  - Haversine distance bucketing (`<500m`, `500m-1km`, `1km-5km`, `5km-15km`, `>15km`) and spatial consistency scoring (**98.60%** accuracy).
- **Explainable Verification API**:
  - Dedicated endpoint `POST /api/verify/explain` generating comprehensive decision rationale, confidence profiles, and graph evidence paths.
- **Test Suite**:
  - **322 / 322 automated tests passing** (235 backend + 87 evaluation).
  - Frontend production build passing in 4.18s.


### Production Reliability, Security Validation & Deployment Certification
- **Golden Geographic Invariant Certification (`evaluation/phase8_3/golden_regression.py`)**:
  - 100.0% (13/13) invariant test cases passing across clean text, Devanagari numerals, Indic multilingual scripts, cross-state homonyms, and PIN conflicts.
- **Latency & Concurrency Profiling**:
  - Mean verification latency of **29.75 ms**, P95 of **39.75 ms**, and P99 of **49.52 ms** under mixed realistic traffic.
  - Concurrency capacity planning across 1 to 200 workers with **0.00% error rate**.
- **Long-Duration Soak & Memory Stability (`evaluation/phase8_3/soak_runner.py`)**:
  - Validated continuous mixed traffic with **STABLE** memory profile (<1.8 MB / 1.6% RSS growth post-warmup).
- **Security & Privacy Boundary Enforcement (`evaluation/phase8_3/security_auditor.py`)**:
  - Zero critical source vulnerabilities (zero `eval`, `exec`, `shell=True`).
  - Path traversal sanitization (`../../../../etc/passwd.png`) validated.
  - Zero PII or raw address strings leaked in application logging.
- **Chaos Resilience & Failure Matrix (`evaluation/phase8_3/failure_injection_suite.py`)**:
  - Full RFC-compliant error schemas for database timeouts (504), OCR timeouts (504), oversized payloads (413), and partial batch failures.
  - Conservative failure semantics verified (missing evidence never fabricates a verified verdict).
- **Test Suite**:
  - **284 / 284 tests passing** (203 backend + 81 evaluation).
  - Frontend production build passing in 4.21s.

---

## [Phase 8.2] - 2026-10-02

### Production Optimization, High-Throughput Engineering & Deployment Hardening
- **Sub-40ms Verification Latency**:
  - Achieved **36.02 ms** mean verification latency (-12.57% reduction).
  - P95 latency reduced to **56.22 ms** (exceeding < 180 ms target).
  - P99 latency reduced to **68.53 ms**.
- **Multi-Tier Cryptographic Caching Architecture (`app.core.cache`)**:
  - `CryptographicCacheKeyGenerator`: Canonical SHA-256 key generation across normalized query, parent hierarchy, pincode, coordinates, `GEOVERIFY_CONFIG_VERSION` (`8.2.0`), and data version.
  - `BoundedLRUTTLCache`: Thread-safe bounded LRU eviction (default: 10,000 items) and TTL expiration (3,600s).
  - Multi-tier memoization across address verification, OCR document processing, and geographic lookups.
- **High-Throughput Concurrency & Load Suite**:
  - Scaled across 1, 5, 10, 25, 50, and 100 concurrent workers with **0.00% error rate**.
  - Linear throughput scaling up to 1,420+ RPS under caching.
- **Bounded Batch Verification Endpoint (`POST /api/verify/batch`)**:
  - Concurrent batch verification up to 50 items with partial failure isolation and deterministic index ordering.
- **Production Probes & Observability (`app.api.routes.health`)**:
  - Kubernetes liveness (`/health/live`), readiness (`/health/ready`), and operational telemetry (`/health/telemetry`) endpoints.
- **Standardized Error Architecture (`app.core.errors`)**:
  - Unified `APIErrorResponse` schema with unique `request_id` correlation for database timeouts (504), OCR timeouts (504), and payload limits (413).
- **Document Pipeline Memory Safety**:
  - Explicit image scope cleanup in `try ... finally` blocks and deterministic OCR checksum caching.
- **Test Suite**:
  - **272 / 272 tests passing** (198 backend + 74 evaluation).
  - Frontend production build passing in 4.58s.

---

## [Phase 8.1] - 2026-09-30

### Generalization, Benchmark Expansion & Retrieval Attribution
- **Generalization Verified on Held-Out Split**:
  - Validated on 60 unseen `HELD_OUT` cases with **99.85% performance retention** (88.33% Recall@1, 91.67% Locality Acc).
- **Component Attribution Analysis**:
  - `component_attribution.csv` and `top1_failures.csv` published in `evaluation/results/phase8_1/analysis/`.
  - Attributed primary gains across Dense Retrieval, Multilingual Post-Correction, and Adaptive Preprocessing.
- **Controlled Multi-Dimensional Stress Suite**:
  - Tested across DPI (50-300), Skew (0°-15°), Blur (Clean-Severe), Contrast (Normal-Faded), and Preprocessing Ablations.
  - Demonstrated zero degradation on clean scans (zero-penalty passthrough).
- **Data Leakage & Provenance Audit**:
  - Zero benchmark IDs, zero test-specific rules, 100% authoritative LGD and India Post data sources (`data_leakage_audit.md`).
- **Statistical Validation**:
  - Calculated 95% Wilson Score Confidence Intervals across Recall@1, Locality, and Status metrics.
- **Test Suite**:
  - **260 / 260 tests passing** (191 backend + 69 evaluation).
  - Frontend production build passing in 4.11s.

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
