# Phase 10.2 Gate 2: Metric Definition & Denominator Integrity Audit

## 1. Overview
To ensure complete scientific rigor and eliminate evaluation ambiguity across historical and current benchmarks, this document establishes the precise mathematical formulation, numerator, denominator, eligibility criteria, and interpretation for all GeoVerify evaluation metrics.

---

## 2. Formal Metric Definitions

### A. Candidate Retrieval Metrics

| Metric | Mathematical Formula | Eligible Population | Target / Interpretation |
| :--- | :--- | :--- | :--- |
| **Recall@1 (R@1)** | $\frac{1}{N} \sum_{i=1}^N \mathbb{I}(\text{Rank}(\text{Target}_i) = 1)$ | All $N=5,000$ cases | Percentage of cases where true ground-truth entity is ranked at position 1. |
| **Recall@5 (R@5)** | $\frac{1}{N} \sum_{i=1}^N \mathbb{I}(\text{Rank}(\text{Target}_i) \le 5)$ | All $N=5,000$ cases | Percentage of cases where true ground-truth entity appears in top 5 candidates. |
| **Recall@10 (R@10)**| $\frac{1}{N} \sum_{i=1}^N \mathbb{I}(\text{Rank}(\text{Target}_i) \le 10)$| All $N=5,000$ cases | Percentage of cases where true ground-truth entity appears in top 10 candidates. |
| **MRR** | $\frac{1}{N} \sum_{i=1}^N \frac{1}{\text{Rank}(\text{Target}_i)}$ | All $N=5,000$ cases (0 if not in Top-K) | Mean Reciprocal Rank across the candidate pool. |

---

### B. Geographic Administrative Extraction Metrics

| Metric | Definition & Matching Criteria | Exclusions / Denominator |
| :--- | :--- | :--- |
| **Locality Accuracy** | Substring / canonical equality between predicted locality and ground truth. | $N=5,000$ cases |
| **District Accuracy** | Canonical equality between predicted administrative district and ground truth. | $N=5,000$ cases |
| **State Accuracy** | Canonical equality between predicted state and ground truth. | $N=5,000$ cases |
| **PIN Accuracy** | Strict 6-digit match between predicted PIN and ground truth PIN. | $N=5,000$ cases |
| **Exact Hierarchy Accuracy**| Simultaneous exact match of State, District, and Locality. | $N=5,000$ cases |

---

### C. Decision & Safety Metrics

| Metric | Formula / Definition | Rationale |
| :--- | :--- | :--- |
| **Status Accuracy** | $\frac{1}{N} \sum_{i=1}^N \mathbb{I}(\text{PredictedStatus}_i = \text{ExpectedStatus}_i)$ | Primary operational decision metric across `VERIFIED`, `CONSISTENT`, `NEEDS_REVIEW`, `INCONSISTENT`, `AMBIGUOUS`. |
| **Ambiguity F1** | $2 \cdot \frac{\text{Precision}_{\text{amb}} \cdot \text{Recall}_{\text{amb}}}{\text{Precision}_{\text{amb}} + \text{Recall}_{\text{amb}}}$ | Balances precision of flagging homonyms vs false alarms on clear addresses. |
| **False High Confidence** | Count of cases where $\text{Confidence} \ge 0.85$ but $\text{PredictedStatus} \ne \text{ExpectedStatus}$. | Primary safety invariant: must remain as close to 0 as possible. |

---

### D. Probabilistic Calibration Metrics

| Metric | Formula | Interpretation |
| :--- | :--- | :--- |
| **Brier Score** | $\frac{1}{N} \sum_{i=1}^N (p_i - y_i)^2$ | Mean squared error between predicted confidence probability $p_i$ and binary correctness $y_i \in \{0, 1\}$. |
| **Expected Calibration Error (ECE)** | $\sum_{m=1}^M \frac{|B_m|}{N} |\text{acc}(B_m) - \text{conf}(B_m)|$ | Weighted average absolute difference between accuracy and mean confidence across $M=10$ probability bins. |

---

## 3. Denominator Rule
Every metric reported in Phase 10.2 uses the full frozen population denominator ($N=5,000$) unless explicitly stated otherwise (e.g. subgroup analyses clearly specifying their partition size $N_{\text{sub}}$).
