# Verification Decision Engine Calibration & Score Bands

## 1. Decision Engine Calibration Overview

The GeoVerify Decision Engine evaluates geographic evidence generated across 5 dimensions:
1. **Administrative Hierarchy Alignment**: State → District → Sub-District consistency.
2. **PIN Code Boundary Verification**: Point-in-polygon and postal database validation.
3. **Locality & Street Entity Resolution**: Multi-stage fuzzy retrieval and context-aware ranking.
4. **Address Completeness**: Structural completeness and premise presence.
5. **Ambiguity & Penalty Deductions**: Multiple plausible geographic matches or name collisions.

---

## 2. Calibrated Status Thresholds & Score Bands

| Score Band | Standard Status | Description | Action Required |
| :--- | :--- | :--- | :--- |
| **85 – 100** | `VERIFIED` | Full geographic consistency across all hierarchy levels, PIN verified, exact locality match, high completeness. | Automated Approval |
| **70 – 84** | `CONSISTENT` | Valid geographic hierarchy and PIN match, but partial premise data or minor phonetic deviation. | Automated Approval (Low Risk) |
| **55 – 69** | `NEEDS_REVIEW` | Borderline confidence, unverified sub-district, or multiple competing candidates in close proximity. | Manual Operator Review |
| **40 – 54** | `AMBIGUOUS` | High-confidence candidates found in different districts/states (e.g. Rampur, UP vs Rampur, Bihar). | Disambiguation Prompt |
| **0 – 39** | `INCONSISTENT` | Geographic contradiction detected (e.g. PIN points to Pune, Maharashtra, but text specifies Jaipur, Rajasthan). | Immediate Rejection |
| **N/A (No Match)**| `UNABLE_TO_VERIFY`| Input text or image unparseable, unreadable OCR noise, or empty address segment. | Resubmission Request |

---

## 3. Score Band Calibration & Empirical Accuracy

Evaluating the 260 Phase 7.2 benchmark cases across score bands:

| Score Band | Sample Count | Correct Status Count | Accuracy (%) | Primary Observed Failure Modes |
| :--- | :--- | :--- | :--- | :--- |
| **85 – 100** | 148 | 138 | **93.24%** | Minor locality boundary overlap (rural fringe). |
| **70 – 84** | 44 | 36 | **81.82%** | Omitted street tokens misclassified as conflict. |
| **61 – 70** | 22 | 16 | **72.73%** | Ambiguity threshold sensitivity. |
| **41 – 60** | 18 | 13 | **72.22%** | Boundary cases between review and inconsistent. |
| **21 – 40** | 16 | 14 | **87.50%** | Clear administrative contradiction. |
| **0 – 20** | 12 | 11 | **91.67%** | Fabricated PINs or non-existent states. |
| **Total** | **260** | **228** | **87.69%** | |

---

## 4. Calibrated Decision Rules

1. `RULE_PERFECT_MATCH`: Score $\ge 85$, PIN matched, hierarchy consistent, completeness $\ge 0.70 \implies$ `VERIFIED`.
2. `RULE_PARTIAL_CONSISTENT`: Score $\ge 70$, PIN matched, hierarchy consistent, missing premise without contradictions $\implies$ `CONSISTENT`.
3. `RULE_AMBIGUITY_DETECTED`: Score gap between candidate 1 and candidate 2 $< 0.10$ and candidates belong to different administrative parents $\implies$ `AMBIGUOUS`.
4. `RULE_HIERARCHY_CONTRADICTION`: PIN district does not match claimed district and distance $> 50\text{ km} \implies$ `INCONSISTENT`.
5. `RULE_SEVERE_NOISE`: Token recognition confidence $< 0.30$ or unparsed characters $> 70\% \implies$ `UNABLE_TO_VERIFY`.
