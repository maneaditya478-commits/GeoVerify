# GeoVerify India — Phase 10.1: Calibration Metric Reconciliation

## 1. Background & Context

The Phase 10 independent report presented three calibration measurements across different stages:
1. **Phase 9 Validation Brier Score**: `0.0270` (Measured during 7-stage ablation progression EXP_G on 4-state domain).
2. **Phase 9 Dedicated Calibrated Brier Score**: `0.0171` (Measured on 400-case held-out partition in `test_phase9_calibration.py`).
3. **Phase 10 Independent Calibrated Brier Score**: `0.1547` (Expected Calibration Error: `0.1794` across 5,000 national independent cases).

---

## 2. Mathematical Metric Definitions & Evaluation Populations

### 2.1 Brier Score
The Brier score measures the mean squared difference between predicted confidence $p_i \in [0, 1]$ and actual binary outcome $y_i \in \{0, 1\}$ ($y_i = 1$ if verification status matches ground truth, $0$ otherwise):
$$\text{Brier} = \frac{1}{N} \sum_{i=1}^N (p_i - y_i)^2$$

### 2.2 Expected Calibration Error (ECE)
Samples are partitioned into $M=10$ equally spaced confidence bins $B_m = (\frac{m-1}{M}, \frac{m}{M}]$:
$$\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$
where $\text{acc}(B_m) = \frac{1}{|B_m|} \sum_{i \in B_m} y_i$ and $\text{conf}(B_m) = \frac{1}{|B_m|} \sum_{i \in B_m} p_i$.

---

## 3. Reconciliation & Distribution-Shift Findings

| Calibration Evaluation | Population ($N$) | Geographic Scope | Settlement Types | Uncalibrated Brier | Calibrated Brier | Calibrated ECE |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Phase 9 Calibration** | 400 | 4 States (MH, KA, DL, TS) | Metro / Urban | 0.0450 | **0.0171** | **0.0210** |
| **Phase 9 Ablation (EXP_G)**| 2,000 | 4 States | Metro / Urban | 0.0520 | **0.0270** | **0.0310** |
| **Phase 10 Independent** | 5,000 | 36 States/UTs (All 7 Zones) | Metro, Urban, Semi, Rural, Tribal | 0.1857 | **0.1547** | **0.1794** |

### Why Did ECE and Brier Shift in Phase 10?
1. **Uncalibrated Distribution Shift**: Isotonic parameters were fitted on urban/metro addresses where candidate retrieval recall was $>95\%$.
2. **Candidate Retrieval Decoupling**: When a rural/tribal locality was missing from the gazetteer, candidate confidence was low ($<0.20$), yet certain high-level geographic consistency signals (like a valid state or PIN) partially inflated intermediate scores.
3. **Safety Invariant Preserved**: Critically, the system maintained a **0.00% False-High-Confidence rate** (i.e. zero cases where $p_i > 0.80$ while decision was wrong).
