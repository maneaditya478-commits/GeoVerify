# Phase 10.1 Component Ablation Study & Attribution Analysis

## 1. Overview
To systematically quantify the contribution of each architectural component to generalization gap recovery, a 7-stage ablation suite (**EXP_A** through **EXP_G**) was executed across a 400-case validation partition.

---

## 2. Experimental Ablation Configuration

| Experiment ID | Configuration Description | Disabled Component |
| :--- | :--- | :--- |
| **EXP_A (Full)** | Complete Phase 10.1 Production Architecture | None (Full System Baseline) |
| **EXP_B** | Dense / Trigram Geographic Retrieval Disabled | Lexical Fuzzy Only |
| **EXP_C** | Spatial Proximity & Bounding Box Filtering Disabled | Geometry Engine Disabled |
| **EXP_D** | Temporal Geographic Reasoning Disabled | Historical Entity Resolution Disabled |
| **EXP_E** | Pan-Indic Multilingual Normalization Disabled | English Latin Exact Only |
| **EXP_F** | Homonymous Ambiguity Engine Disabled | First Candidate Forced |
| **EXP_G** | Probabilistic Confidence Calibration Disabled | Raw Score Thresholds |

---

## 3. Empirical Ablation Results

| Experiment | Recall@1 (%) | Recall@5 (%) | Exact Hierarchy (%) | Status Accuracy (%) | Ambiguity F1 | Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EXP_A (Full System)** | **88.25** | **98.50** | **84.50** | **86.75** | **0.8842** | **31.4** |
| **EXP_B (-Dense Retrieval)** | 64.50 | 79.25 | 58.00 | 66.25 | 0.8120 | 24.1 |
| **EXP_C (-Spatial Filter)** | 78.00 | 91.00 | 72.25 | 77.50 | 0.8250 | 28.6 |
| **EXP_D (-Temporal Engine)** | 81.25 | 93.75 | 76.50 | 79.25 | 0.8510 | 29.8 |
| **EXP_E (-Pan-Indic Normalizer)**| 56.75 | 71.50 | 50.25 | 58.00 | 0.7630 | 22.3 |
| **EXP_F (-Ambiguity Engine)** | 86.50 | 97.25 | 79.00 | 69.50 | 0.0000 | 26.2 |
| **EXP_G (-Confidence Model)** | 88.25 | 98.50 | 84.50 | 74.00 | 0.8842 | 29.5 |

---

## 4. Key Attribution Takeaways
1. **Pan-Indic Multilingual Normalization (+31.5% Recall@1)**: Disabling Pan-Indic normalization caused the single largest performance drop on non-Latin addresses, confirming that Unicode-range expansion across Dravidian and Eastern Indic scripts was a critical factor in closing the Phase 10 generalization gap.
2. **Dense N-Gram Retrieval (+23.75% Recall@1)**: Crucial for degraded OCR and token boundary splits (e.g. *"Koth rud"* or *"Khar adi"*), preventing zero-retrieval dropouts.
3. **Homonymous Ambiguity Engine (+17.25% Status Accuracy)**: Without conservative ambiguity detection, forced candidate selection caused misclassification of homonyms (*Rampur*, *Bilaspur*, *Fatehpur*), collapsing Ambiguity F1 to 0.0.
4. **Probabilistic Calibration (+12.75% Status Accuracy)**: Ensured low-evidence and partially conflicting records were appropriately categorized as `NEEDS_REVIEW` or `INCONSISTENT` rather than falsely verified with manufactured certainty.
