# GeoVerify India — Performance Profiling & Latency Breakdown (Phase 6.1)

## Overview

GeoVerify India is designed for high-throughput geographic verification and KYC/onboarding pipelines. Phase 6.1 profiled every sub-component of the verification pipeline across multiple repetitions to eliminate hot-spots, reduce memory allocations, and establish latency baselines before Phase 7 OCR integration.

---

## 1. Latency Breakdown by Pipeline Component

Measured across 30 full-pipeline repetitions with warmup:

| Pipeline Stage | Mean Latency (ms) | Std Dev (ms) | P50 (ms) | P95 (ms) | P99 (ms) | Optimization Applied |
|---|---|---|---|---|---|---|
| `normalization` | 0.107 | 0.119 | 0.081 | 0.179 | 0.313 | Compiled regex patterns |
| `parsing` | 0.495 | 0.526 | 0.437 | 0.780 | 1.227 | Fast tokenization & state anchoring |
| `candidate_generation` | 12.168 | 3.723 | 11.601 | 14.956 | 17.180 | In-memory hash maps for exact/alias/prefix |
| `ranking` | 0.351 | 0.177 | 0.322 | 0.675 | 0.859 | Vectorized feature scoring |
| `hierarchy_validation` | **0.047** | 0.020 | 0.044 | 0.086 | 0.119 | **$O(1)$ dictionary lookups (70% speedup)** |
| `boundary_pip` | 0.790 | 0.199 | 0.686 | 1.185 | 1.422 | Shapely STRtree spatial indexing |
| `pin_validation` | 0.045 | 0.012 | 0.041 | 0.065 | 0.090 | Hash-indexed PIN directory |
| `nearby_search` | 0.065 | 0.024 | 0.055 | 0.099 | 0.170 | Spatial radius indexing |
| `ambiguity_detection` | 0.023 | 0.008 | 0.020 | 0.033 | 0.059 | Delta score thresholding |
| `evidence_generation` | 0.045 | 0.017 | 0.038 | 0.075 | 0.120 | Rule-based accumulator |
| `evidence_graph` | 0.119 | 0.039 | 0.102 | 0.205 | 0.278 | Directed graph serialization |
| `decision_engine` | 0.011 | 0.003 | 0.010 | 0.018 | 0.021 | Deterministic rule matrix |
| **End-to-End Pipeline** | **35.02** | **11.55** | **32.25** | **62.50** | **77.70** | Full resolution & verification |

---

## 2. In-Memory Indexing Architecture

To avoid $O(N)$ linear scans across thousands of Indian localities, districts, and PIN codes, the following in-memory indices were implemented:

1. **`_state_index` & `_district_index` in `hierarchy.py`**:
   - Maps normalized state and district names to canonical objects in $O(1)$ time.
   - Handles multi-language names and historical aliases (e.g. Bangalore $\rightarrow$ Bengaluru Urban).

2. **`locality_by_name` & `locality_by_alias` in `candidates.py`**:
   - Maps canonical NFKC normalized strings to locality records.
   - Bypasses string fuzzy iteration when exact or alias match exists.

3. **`pincodes_by_prefix` in `candidates.py`**:
   - Groups 6-digit PIN codes by 2-digit postal circle prefixes (e.g. "40", "41" for Maharashtra).
   - Constrains circle searches to relevant regional subsets.

---

## 3. SLA Compliance & Throughput

- **Mean Latency SLA**: $<50.0 \text{ ms}$ (Achieved: **35.02 ms**).
- **P95 Latency SLA**: $<100.0 \text{ ms}$ (Achieved: **62.50 ms**).
- **P99 Latency SLA**: $<150.0 \text{ ms}$ (Achieved: **77.70 ms**).
- **Target Throughput**: $>25 \text{ requests/sec/core}$ on standard commodity CPU.
