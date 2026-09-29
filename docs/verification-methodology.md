# Verification Methodology & Scoring Model

## 1. Core Principles

GeoVerify India operates on an evidence-based multi-signal model. An address is never marked as fraudulent simply because of minor formatting variations or missing optional fields.

## 2. Consistency Scoring Framework

The **Geographic Consistency Score** is a deterministic, transparent score ranging from $0$ to $100$:

$$\text{Score} = S_{\text{hierarchy}} + S_{\text{boundary}} + S_{\text{locality}} + S_{\text{pincode}} + S_{\text{geocoding}} + S_{\text{nearby}}$$

| Signal Layer | Max Weight | Verification Criteria |
| :--- | :---: | :--- |
| **Administrative Hierarchy** | 25 | Validates parent-child alignment between country, state, district, and taluka. |
| **Geographic Boundary Match** | 25 | Confirms point coordinates fall inside authoritative district and state polygons. |
| **Locality Match** | 20 | Confirms locality / village exists within the asserted jurisdiction. |
| **PIN Code Consistency** | 15 | Validates 6-digit postal format, postal circle prefix, and centroid distance $\le 20\text{ km}$. |
| **Geocoding Quality** | 10 | Granularity and confidence of resolved spatial coordinates. |
| **Nearby Context** | 5 | Presence of verified contextual infrastructure (transit, hospitals, public services). |
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
