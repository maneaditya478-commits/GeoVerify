# GeoVerify India — Phase 10.1: OCR Robustness & Partial Address Analysis

## 1. Executive Summary

The Phase 10 degradation curve revealed that under moderate-to-severe OCR degradation (Levels 2–4), Recall@1 dropped from 38.00% (Clean) to 4.70% (Level 3) and 1.50% (Level 4).

---

## 2. Controlled OCR Distortion Model

| OCR Tier | Distortion Profile | Character Error Rate (CER) | Word Error Rate (WER) | Primary Failure Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **Level 0 (Clean)** | Synthetic digital text, 0 noise | 0.0% | 0.0% | Reference baseline |
| **Level 1 (Mild)** | Light blur, 5° skew, slight contrast fade | 2.5% | 6.0% | Minor single-character misrecognitions |
| **Level 2 (Moderate)** | Salt-and-pepper noise, folds, 15° skew | 8.0% | 18.5% | Punctuation loss, token merging |
| **Level 3 (Severe)** | Heavy bleed, watermarks, character drops | 22.0% | 45.0% | Broken entity stems, dropped vowels |
| **Level 4 (Occluded)** | Missing 50% tokens, heavy speckle | 48.0% | 72.0% | Truncated addresses, isolated numbers |

---

## 3. Core Architectural Principle: Missing vs Conflicting Evidence

GeoVerify maintains the fundamental principle established in Phase 7.3:
> **Missing evidence is not conflicting evidence.**

Under severe OCR degradation:
1. An unextracted house or street number does **not** make an address `INCONSISTENT`.
2. A missing subdistrict does **not** invalidate an established Locality $\to$ District $\to$ State relationship.
3. If an OCR extraction is too noisy to resolve any administrative entity, the system outputs `UNABLE_TO_VERIFY` with low confidence rather than fabricating a false decision.
