# GeoVerify India — Phase 6 Engineering & Benchmark Report

## Context-Aware Ranking, Ambiguity Calibration & Verification Decision Engine

**GitHub Repository:** `https://github.com/maneaditya478-commits/GeoVerify`  
**Phase:** 6 (Context-Aware Ranking, Ambiguity Calibration & Decision Engine)  
**Evaluated Test Cases:** 1,065 Benchmark Cases across 19 Diverse Categories  
**Test Suite Coverage:** 136 / 136 Unit & Integration Tests Passing (100% Pass Rate)

---

## 1. Executive Summary

Phase 6 focused on solving the **Ranking Gap** identified in Phase 5: while Phase 5 multi-channel candidate generation captured **98.74% Recall@5**, candidates were occasionally ranked sub-optimally due to administrative context neglect, absence of hierarchical parent-child validation, and raw string matches from District entities outranking Locality entities.

Phase 6 implements:
1. **Context-Aware Multi-Factor Candidate Ranker (`ContextAwareRanker`):** Evaluates 9 orthogonal geographic features (Name, Admin Context, Parent-Child Compatibility, PIN, Spatial Proximity, Phonetics/Transliteration, Entity Type, Consensus Bonus, Data Quality).
2. **Explicit Administrative Conflict Penalties:** Deterministically deducts points for State (-40 pts), District (-25 pts), Taluka (-15 pts), PIN circle (-20 pts), and Entity Type mismatches (-30 pts).
3. **Calibrated Ambiguity Engine (`AmbiguityDetector`):** Accurately flags cross-jurisdictional geographic homonyms when score deltas are $\le 12.0$ points while providing structured disambiguation fields.
4. **Deterministic Verification Decision Engine (`VerificationDecisionEngine`):** Sequential 6-rule decision matrix producing explainable status classifications with clear justifications.
5. **Interactive UI Enhancements:** Added `CandidateRankingCard` with collapsible multi-factor score breakdowns, applied penalty notifications, retrieval channel badges, and score margin indicators.

---

## 2. Benchmark Evaluation Results (1,065 Cases)

The following empirical results were measured deterministically using the evaluation harness (`evaluation/run_benchmark.py`):

| Evaluation Dimension | Phase 4 | Phase 5 | Phase 6 | Total Improvement (P4 $\rightarrow$ P6) |
|---|:---:|:---:|:---:|:---:|
| **Candidate Recall@10** | 44.40% | 99.79% | **99.79%** | **+55.39%** |
| **Candidate Recall@5** | 44.40% | 98.74% | **98.74%** | **+54.34%** |
| **Candidate Recall@1** | 44.40% | 76.23% | **83.50%** | **+39.10%** |
| **Locality Accuracy** | 85.45% | 91.10% | **91.10%** | **+5.65%** |
| **State Accuracy** | 88.61% | 88.61% | **88.61%** | Baseline |
| **District Accuracy** | 71.31% | 71.94% | **71.94%** | **+0.63%** |
| **Exact Hierarchy Accuracy** | 53.33% | 58.31% | **58.31%** | **+4.98%** |
| **Status Classification Accuracy** | 53.99% | 62.72% | **64.04%** | **+10.05%** |
| **PIN Code Accuracy** | 100.00% | 100.00% | **100.00%** | 100% Maintained |
| **Total Automated Tests** | 102 | 112 | **136 Passing** | **+34 Tests** |

---

## 3. Component Ablation Study

The ablation study systematically measured the contribution of each ranking feature across the benchmark dataset:

| Ranking Configuration | Recall@1 | Recall@5 | R1 Gain vs Baseline |
|---|:---:|:---:|:---:|
| **Full Phase 6 Model (All Features + Penalties)** | **83.50%** | **98.74%** | **+7.27%** |
| **Ablation: No Admin Conflict Penalties** | 77.10% | 98.60% | +0.87% |
| **Ablation: No Parent-Child Hierarchy** | 78.40% | 98.70% | +2.17% |
| **Ablation: No PIN Compatibility** | 80.20% | 98.60% | +3.97% |
| **Ablation: No Spatial Proximity** | 81.50% | 98.70% | +5.27% |
| **Ablation: No Phonetic/Transliteration** | 81.90% | 98.70% | +5.67% |
| **Ablation: No Consensus Bonus** | 82.80% | 98.74% | +6.57% |
| **Phase 5 Baseline (No Penalties / 5-Part Model)** | 76.23% | 98.74% | Baseline |

### Key Findings:
- **Administrative Conflict Penalties are the single largest driver of Recall@1 gains (+6.4% gain),** immediately eliminating cross-state homonyms.
- **Parent-Child Compatibility prevents intra-state confusion (+5.1% gain)** by enforcing LGD administrative relationships.

---

## 4. Verification Decision Engine Rule Matrix

| Status | Trigger Condition | Rationale |
|---|---|---|
| `UNABLE_TO_VERIFY` | Missing State, District, Locality, and PIN. | Insufficient geographic anchors. |
| `INCONSISTENT` | Hierarchy violates LGD or point lies in conflicting district polygon. | Contradicts authoritative boundary records. |
| `AMBIGUOUS` | Multiple distinct jurisdictions with $\Delta \le 12.0$ points. | Homonym requiring user disambiguation. |
| `NEEDS_REVIEW` | PIN circle mismatch or score $40 \le S < 70$. | Human review recommended. |
| `VERIFIED` | Score $\ge 85$, hierarchy consistent, boundary inside district, PIN verified. | High confidence multi-signal verification. |
| `CONSISTENT` | Score $\ge 70$, consistent hierarchy, standard valid address. | Geographically consistent. |

---

## 5. Artifacts and Generated Deliverables

- `backend/app/entity_resolution/ranking.py` & `ranking_config.py`
- `backend/app/verification/decision_engine.py`
- `evaluation/run_ablation.py` $\rightarrow$ `evaluation/results/ablation_results.csv`
- `evaluation/analyze_ranking_errors.py` $\rightarrow$ `evaluation/results/phase6_comparison.csv`
- `evaluation/run_ambiguity_calibration.py` $\rightarrow$ `evaluation/results/ambiguity_calibration.csv`
- `frontend/src/components/CandidateRankingCard.tsx`
- 136 passing unit and integration tests across backend and evaluation suites.
