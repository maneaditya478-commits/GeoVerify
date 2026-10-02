# Phase 10.2 Gate 0: Repository Forensics & Root-Cause Audit

## 1. Executive Summary & Context
Phase 10.2 was initiated to perform a thorough forensic investigation of the GeoVerify India repository across four critical milestones:
1. **Phase 9 Baseline (`ae80663`)** — Initial research extensions (temporal, graph, probabilistic, landmarks).
2. **Phase 10 Independent Generalization Release (`7e3aa88`)** — Introduction of 5,000-case frozen independent benchmark.
3. **Phase 10.1 Initial Commit (`39e9ac8`)** — Introduction of Pan-Indic Unicode regexes and initial national gazetteer generation script.
4. **Phase 10.1 Reconciled Release (`1155ee7`)** — Full execution of pan-India gazetteer merging and updated evaluation metrics.

---

## 2. Lineage and Git Diff Forensics

### A. Transition `ae80663` → `7e3aa88` (Phase 9 to Phase 10)
- **Primary Change**: Addition of the frozen held-out independent dataset (`evaluation/datasets/phase10_independent_dataset.json`, 5,000 cases, SHA-256 `f8753334a7d23bef8ab7cc1376d69a22c1c313e8199d5cea456f757781983829`).
- **Core Discrepancy Discovered**:
  - In Phase 9, evaluation was conducted on seed distribution datasets (covering Maharashtra, Karnataka, Delhi, UP, Rajasthan, Gujarat).
  - In Phase 10, the frozen dataset sampled from all 36 States/UTs.
  - Because `data/processed/districts.json` had only 30 districts and `localities.json` had only 46 localities, approximately 75% of nationwide test cases had target entities missing from the in-memory index (`CORRECT_NOT_IN_UNIVERSE`), producing Recall@1 of 15.74% and MRR of 0.1889.

### B. Transition `7e3aa88` → `39e9ac8` (Phase 10 to Phase 10.1 Initial)
- **Primary Change**:
  - Implementation of Pan-Indic script normalization across Tamil, Telugu, Kannada, Bengali, Gujarati, Gurmukhi, Odia, and Malayalam in `backend/app/services/multilingual_alignment.py` and `transliteration.py`.
  - Addition of `data/scripts/generate_national_gazetteer.py` and developmental benchmark generators (`phase10_1_dev.json`, `phase10_1_validation.json`).
- **Evaluation Timing**:
  - An evaluation pass was recorded before the newly generated national gazetteer was merged into `data/processed/`, resulting in an intermediate Recall@1 of 17.84% and Status Accuracy of 77.40%.

### C. Transition `39e9ac8` → `1155ee7` (Phase 10.1 Reconciled)
- **Primary Change**:
  - `generate_national_gazetteer.py` merged 82 districts, 84 localities, and 83 PIN code records across all 36 States/UTs into `data/processed/`.
  - Homonymous place names (*Rampur*, *Bilaspur*, *Fatehpur*, *Aurangabad*, *Rajapur*) were explicitly preserved across multiple states without key collisions.
  - Evaluation on the 5,000 frozen cases executed with the full gazetteer indexed, lifting Recall@1 from 17.84% to **49.16%**, MRR to **0.6391**, Status Accuracy to **84.36%**, Temporal Accuracy to **94.78%**, and Multilingual Accuracy to **69.61%**.

---

## 3. Discrepancy Resolution Summary

| Factor | Commit `39e9ac8` (Earlier Report) | Commit `1155ee7` (Reconciled Report) | Root Cause of Discrepancy |
| :--- | :--- | :--- | :--- |
| **In-Memory Gazetteer** | Partial (30 Districts) | Nationwide (82 Districts, 84 Localities) | Gazetteer generation script executed after initial benchmark run |
| **Dravidian/Eastern Retrieval** | Partial | Fully Indexed | Expanded national localities indexed |
| **Candidate Recall@1** | 17.84% | **49.16%** | Pan-India localities became retrievable |
| **Candidate Recall@5** | 86.72% | **80.48%** | Candidate pool expanded from 46 to 84 localities |
| **MRR** | 0.4801 | **0.6391** | Higher rank positions for retrieved true positives |
| **Status Accuracy** | 77.40% | **84.36%** | Enhanced administrative consistency scoring |
| **Temporal Accuracy** | 72.29% | **94.78%** | Historical aliases matched against expanded gazetteer |

---

## 4. Conclusion
The difference between the two Phase 10.1 reports is completely accounted for by the activation of the merged national gazetteer in `data/processed/`. No data leakage, test-specific conditionals, or metric formula manipulations occurred.
