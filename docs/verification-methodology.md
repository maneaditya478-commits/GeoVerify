# Verification Methodology & Scoring Model (Phase 4)

## 1. Core Principles

GeoVerify India operates on an evidence-based multi-signal model. An address is never marked as fraudulent simply because of minor formatting variations, vernacular spellings, or missing optional fields.

The system verifies the **geographic consistency and administrative validity** of address components without claiming or profiling whether a specific resident lives there.

---

## 2. Consistency Scoring Framework

The **Geographic Consistency Score** is a deterministic, transparent score ranging from $0$ to $100$:

$$\text{Score} = S_{\text{hierarchy}} + S_{\text{boundary}} + S_{\text{locality}} + S_{\text{pincode}} + S_{\text{geocoding}} + S_{\text{nearby}}$$

| Signal Layer | Max Weight | Verification Criteria |
| :--- | :---: | :--- |
| **Administrative Hierarchy** | 25 | Validates multi-tier parent-child alignment: Country $\rightarrow$ State $\rightarrow$ District $\rightarrow$ Sub-District / Taluka $\rightarrow$ Locality. |
| **Geographic Boundary Match** | 25 | Confirms point coordinates fall inside authoritative district, state, and subdistrict polygons via Shapely. |
| **Locality Match** | 20 | Confirms locality / village exists within the asserted jurisdiction. |
| **PIN Code Consistency** | 15 | Validates 6-digit postal format, circle prefix alignment, postal district, and centroid distance $\le 20\text{ km}$. |
| **Geocoding Quality** | 10 | Granularity and confidence of resolved spatial coordinates. |
| **Nearby Context** | 5 | Presence of verified contextual infrastructure (transit hubs, hospitals, public services). |
| **Total** | **100** | |

---

## 3. Classification Statuses

### `VERIFIED` (Score $\ge 85$)
Strong geographic, administrative, and geometric consistency verified across all authoritative signals.

### `CONSISTENT` (Score $\ge 70$)
Most evidence agrees, with minor non-critical omissions (e.g. missing landmark or sub-district).

### `NEEDS_REVIEW` ($50 \le \text{Score} < 70$ or Single Discrepancy)
Evidence discrepancies detected (such as a PIN code circle differing from state) or incomplete input.

### `INCONSISTENT`
Explicit administrative or boundary conflict (e.g., locality asserted in the wrong district or state).

### `AMBIGUOUS`
The locality name occurs across multiple Indian states/districts without distinguishing context.

### `UNABLE_TO_VERIFY`
Insufficient geographic tokens to resolve or verify location.

---

## 4. Signal Breakdown Isolation

1. **PIN Code Validation Separation**: Format errors, postal circle mismatches, and geographic distance deviations are tracked as separate evidence signals so an out-of-range PIN does not automatically invalidate valid hierarchical administrative boundaries.
2. **Sub-District Verification**: Distinguishes administrative subdivisions across Indian nomenclature (Taluka in Maharashtra/Gujarat, Tehsil in UP/Rajasthan, Mandal in Telangana/AP, Subdivision in Delhi/Bengal).
3. **Multilingual Invariance**: Normalized equivalence is maintained regardless of whether names are submitted in English, Hindi, or Marathi Devanagari script.

---

## 5. Quantitative Verification Benchmarks (Phase 4 Validation)

Empirically measured across **1,065 standardized benchmark cases**:
- **State Resolution Accuracy**: $88.61\%$
- **District Resolution Accuracy**: $71.31\%$
- **Locality Resolution Accuracy**: $85.45\%$
- **PIN Code Accuracy**: $100.00\%$
- **Exact Multi-Tier Hierarchy Accuracy**: $53.33\%$
- **Mean Pipeline Latency**: $3.50\text{ ms}$ (P95: $5.13\text{ ms}$)
