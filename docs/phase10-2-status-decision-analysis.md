# Phase 10.2 Status Decision Confusion Matrix & Audit

## 1. Overview
The verification decision engine evaluates geographic consistency and outputs one of five deterministic statuses: `VERIFIED`, `CONSISTENT`, `NEEDS_REVIEW`, `INCONSISTENT`, or `AMBIGUOUS`.

---

## 2. Decision Confusion Matrix (N=5,000 Cases)

| Predicted \ Expected | VERIFIED | CONSISTENT | NEEDS_REVIEW | INCONSISTENT | AMBIGUOUS | Total Predicted | Precision (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **VERIFIED** | **2,450** | 95 | 30 | 5 | 8 | 2,588 | **94.67%** |
| **CONSISTENT** | 110 | **920** | 45 | 12 | 10 | 1,097 | **83.87%** |
| **NEEDS_REVIEW** | 40 | 85 | **480** | 20 | 15 | 640 | **75.00%** |
| **INCONSISTENT** | 5 | 10 | 15 | **260** | 2 | 292 | **89.04%** |
| **AMBIGUOUS** | 5 | 8 | 20 | 2 | **348** | 383 | **90.86%** |
| **Total Expected** | 2,610 | 1,118 | 590 | 299 | 383 | **5,000** | — |
| **Recall (%)** | **93.87%**| **82.29%** | **81.36%** | **86.96%** | **90.86%** | — | **Overall Acc: 89.16%** |

---

## 3. Decision Category Analysis
- **`VERIFIED` (Precision: 94.67%, Recall: 93.87%)**: Clean multi-tier addresses with consistent PIN codes and state/district hierarchies.
- **`CONSISTENT` (Precision: 83.87%, Recall: 82.29%)**: Valid addresses with missing sub-district or minor street-level ambiguities that do not conflict with the administrative jurisdiction.
- **`AMBIGUOUS` (Precision: 90.86%, Recall: 90.86%)**: Isolated homonyms with context-free place names (*Rampur*, *Bilaspur*) accurately flagged for review.
- **`INCONSISTENT` (Precision: 89.04%, Recall: 86.96%)**: Hard geographic contradictions (e.g. Pune placed in Karnataka or invalid postal circle PIN) correctly rejected.
