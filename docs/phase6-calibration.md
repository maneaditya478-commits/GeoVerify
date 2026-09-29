# GeoVerify India — Phase 6 Verification Calibration & Scoring Bands

## 1. Overview

Geographic verification requires calibrated thresholds that balance automated acceptance of well-evidenced addresses with appropriate uncertainty flagging for incomplete or ambiguous entries.

Phase 6 introduces a unified calibration methodology connecting:
1. **Multi-Factor Candidate Scores** ($0 - 100$)
2. **Confidence Bands** (`HIGH`, `MEDIUM`, `LOW`)
3. **Ambiguity Delta Margins** ($\Delta \le 12.0$)
4. **Deterministic Status Evaluation Matrix**

---

## 2. Confidence Band Calibration

| Band | Match Score Range | Acceptance Policy | Action |
|---|---|---|---|
| **HIGH Confidence** | $\ge 85.0$ | Automated High Confidence | Safe for automated routing, GIS polygon linkage, and geocoding. |
| **MEDIUM Confidence** | $65.0 - 84.9$ | Automated Standard Consistency | Valid with minor omissions (e.g., missing taluka/landmark). |
| **LOW Confidence** | $< 65.0$ | Flagged for Human Review | Trigger `NEEDS_REVIEW` or `UNABLE_TO_VERIFY`. |

---

## 3. Geographic Consistency Multi-Score Alignment

GeoVerify India computes three complementary, orthogonal score dimensions:

1. **Geographic Consistency Score ($0 - 100$):**
   - Weighted multi-tier GIS signal synthesis: Hierarchy (25%), Boundary (25%), Locality (20%), PIN Code (15%), Geocoding (10%), Nearby (5%).
2. **Address Completeness Score ($0 - 100$):**
   - Structural completeness measuring presence of administrative anchors without penalizing missing house numbers when administrative tokens are verified.
3. **Entity Match Score ($0 - 100$):**
   - Multi-factor candidate ranking score reflecting textual similarity, parent-child compatibility, and consensus across retrieval channels.

---

## 4. Operational Recommendations

- **Automated Verification Workflows:** Addresses achieving status `VERIFIED` or `CONSISTENT` with `HIGH` confidence can proceed without human intervention.
- **Ambiguous Workflows:** Addresses flagged with `AMBIGUOUS` should present the structured `suggested_disambiguations` to the end-user (e.g. asking for State or PIN code).
- **Fraud & Residency Clarification:** In adherence to GeoVerify India core principles, scores strictly evaluate geographic and administrative consistency of the address text itself, never claiming residency or individual person existence.
