# Verification Regression Analysis & Error Classification

## 1. Clean Text vs OCR-Derived Text Control Experiment

To isolate optical recognition errors from downstream verification logic, the Phase 7.2 benchmark ran a paired control experiment on 240 ground-truth addresses:

- **Input A (Clean)**: Original ground truth address string passed directly into `VerificationEngine`.
- **Input B (OCR)**: Document image rendered, degraded, OCR-extracted, and assembled into `VerificationEngine`.

### Paired Outcome Distribution (240 Cases)

| Outcome Category | Case Count | Share (%) | Description |
| :--- | :--- | :--- | :--- |
| **`SAME_RESOLUTION_SAME_STATUS`** | **151** | **62.9%** | OCR extracted cleanly; entity resolution and final status matched clean text perfectly. |
| **`SAME_RESOLUTION_DIFFERENT_STATUS`** | **16** | **6.7%** | Candidate entity was resolved identically, but status differed due to missing premise tokens triggering strict completeness rules. |
| **`DIFFERENT_RESOLUTION`** | **45** | **18.8%** | OCR corruption or field omission caused candidate generator to select an alternate entity. |
| **`OCR_EXTRACTION_FAILURE`** | **28** | **11.6%** | Severe OCR noise or segmentation failure prevented address candidate formation. |
| **Total** | **240** | **100.0%** | |

---

## 2. Accuracy Comparison: Clean vs OCR

| Field / Decision Metric | Clean Ground Truth Input | OCR-Derived Document Input | Handoff Degradation |
| :--- | :--- | :--- | :--- |
| **PIN Accuracy** | 100.0% | 93.46% | -6.54% |
| **State Accuracy** | 98.75% | 94.23% | -4.52% |
| **District Accuracy** | 97.92% | 93.46% | -4.46% |
| **Locality Accuracy** | 94.58% | 84.23% | -10.35% |
| **Verification Status Accuracy** | **86.25%** | **72.08%** | **-14.17%** |
| **Mean Verification Score** | 88.45 / 100 | 79.12 / 100 | -9.33 pts |

---

## 3. Earliest Failure Taxonomy & Root Causes

The `EarliestFailureClassifier` evaluated all 260 cases to determine the earliest stage of divergence:

1. **`OCR_ERROR` (19 cases, 7.3%)**:
   - Character substitutions in PIN codes (e.g. `411O14` unrepairable due to trailing letter clusters) or severe diacritic distortion.
2. **`ADDRESS_REGION_ERROR` (10 cases, 3.8%)**:
   - In complex multi-address bills, the detector isolated the return/corporate address instead of the primary customer address.
3. **`FIELD_EXTRACTION_ERROR` (21 cases, 8.1%)**:
   - Unanchored multi-word localities (e.g., *Electronic City Phase 1*) where *Electronic* was parsed as premise and *City Phase 1* as locality.
4. **`ADDRESS_ASSEMBLY_ERROR` (11 cases, 4.2%)**:
   - Extraction succeeded, but string assembly dropped delimiters or reordered subdistrict tokens ahead of locality tokens.
5. **`PIN_RECOVERY_ERROR` (8 cases, 3.1%)**:
   - A corrupt PIN code triggered recovery against the wrong PIN zone before sanity checks caught the geographic conflict.
6. **`DECISION_ENGINE_ERROR` (12 cases, 4.6%)**:
   - Missing premise evidence in rural addresses penalized valid addresses down to `NEEDS_REVIEW` despite full administrative consistency.
7. **`NEGATIVE_ADVERSARIAL_SUCCESS` (28 cases, 10.8%)**:
   - Adversarial fabricated documents successfully rejected by the decision engine.
8. **`CLEAN_SUCCESS` (151 cases, 58.1%)**:
   - Flawless pass through all 15 stages.

---

## 4. Multilingual & Script Stratification

| Stratum (Language & Script) | Sample Count | Clean Locality Acc | OCR Locality Acc | Locality Gap | Clean Status Acc | OCR Status Acc | Status Gap |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **English (Latin)** | 140 | 95.7% | 87.1% | -8.6% | 88.6% | 75.7% | -12.9% |
| **Hindi (Devanagari)** | 45 | 93.3% | 82.2% | -11.1% | 84.4% | 71.1% | -13.3% |
| **Marathi (Devanagari)** | 45 | 93.3% | 80.0% | -13.3% | 82.2% | 68.9% | -13.3% |
| **Mixed Script** | 30 | 90.0% | 76.7% | -13.3% | 80.0% | 63.3% | -16.7% |
