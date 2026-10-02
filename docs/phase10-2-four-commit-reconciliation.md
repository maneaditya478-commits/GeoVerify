# Phase 10.2 Four-Commit Reproducibility & Metric Reconciliation Report

## 1. Executive Summary
This document establishes the official four-commit reproducibility audit for **GeoVerify India** across Phases 9, 10, 10.1 (initial), and 10.1 (reconciled).

All four milestones were evaluated against the exact same frozen 5,000-case independent benchmark:
- **Path**: `evaluation/datasets/phase10_independent_dataset.json`
- **Total Cases**: 5,000
- **SHA-256**: `f8753334a7d23bef8ab7cc1376d69a22c1c313e8199d5cea456f757781983829`
- **Isolation Status**: `FROZEN_HELD_OUT_IMMUTABLE`

---

## 2. Four-Commit Reproducibility Matrix

| Milestone | Commit | Date | R@1 (%) | R@5 (%) | R@10 (%) | MRR | Locality (%) | District (%) | State (%) | PIN (%) | Status (%) | Temporal (%) | Landmark (%) | Brier | ECE | Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Phase 9 Baseline** | `ae80663` | 2026-10-02 | 15.74 | 25.00 | 25.00 | 0.1889 | 39.42 | 37.42 | 34.84 | 65.54 | 59.38 | 77.73 | 98.00 | 0.1857 | 0.1547 | 44.53 |
| **Phase 10 Release** | `7e3aa88` | 2026-10-02 | 15.74 | 25.00 | 25.00 | 0.1889 | 39.42 | 37.42 | 34.84 | 65.54 | 59.38 | 77.73 | 98.00 | 0.1857 | 0.1547 | 44.53 |
| **Phase 10.1 Initial** | `39e9ac8` | 2026-10-02 | 17.84 | 86.72 | 86.96 | 0.4801 | 86.42 | 41.84 | 35.92 | 65.54 | 77.40 | 72.29 | 0.00 | 0.1679 | 0.1006 | 37.91 |
| **Phase 10.1 Reconciled**| `1155ee7` | 2026-10-02 | **49.16** | **80.48** | **82.68** | **0.6391** | **84.86** | **41.84** | **35.92** | **65.54** | **84.36** | **94.78** | **0.00** | **0.1125** | **0.1808** | **61.82** |

---

## 3. Metric Reconciliation Analysis

### A. Candidate Retrieval (R@1: 15.74% → 49.16%)
- In Phase 9 and Phase 10, candidate retrieval was severely constrained by the in-memory gazetteer containing only 30 districts and 46 localities in 7 states.
- When Phase 10.1 merged national administrative hubs (82 districts, 84 localities) covering all 36 States/UTs, Candidate Recall@1 increased from 15.74% to **49.16%**, and MRR rose from 0.1889 to **0.6391**.

### B. Status Accuracy (59.38% → 84.36%)
- Grounding entities against their authoritative parent states and districts eliminated false positive jurisdictional contradictions on valid national addresses, boosting verification status accuracy to **84.36%**.

### C. Temporal Resolution (77.73% → 94.78%)
- Expanding historical name aliases (*Bombay/Mumbai*, *Poona/Pune*, *Allahabad/Prayagraj*, *Faizabad/Ayodhya*, *Calcutta/Kolkata*, *Madras/Chennai*, *Bangalore/Bengaluru*) across national administrative entities raised temporal accuracy to **94.78%**.

### D. Landmark POI Matching
- Phase 9/10 recorded 98.00% under relaxed semantic vicinity scoring.
- Phase 10.1 evaluated landmark accuracy under strict named POI ID matching where the 5,000 general residential/commercial addresses lacked explicit campus POI IDs. This reconciliation is documented in `docs/phase10-2-landmark-reconciliation.md`.

---

## 4. Machine-Readable Manifest
The full matrix is stored at:
`evaluation/results/phase10_2/reproducibility/four_commit_matrix.json`
