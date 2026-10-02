# Phase 10.2 Gate 3: Candidate Universe & Ranking Bottleneck Audit

## 1. Executive Summary
A comprehensive candidate universe classification was performed across all $N=5,000$ cases of the frozen Phase 10 independent benchmark (`f8753334a7d23bef8ab7cc1376d69a22c1c313e8199d5cea456f757781983829`).

---

## 2. Candidate Universe Distribution (Categories A to G)

| Category | Description | Count (Cases) | Proportion (%) | Diagnostic Meaning |
| :--- | :--- | :--- | :--- | :--- |
| **Category B** | `CORRECT_RETRIEVED_RANK_1` | **3,910** | **78.20%** | Correct geographic entity retrieved and ranked at #1 position. |
| **Category C** | `CORRECT_RETRIEVED_RANK_2_5` | **506** | **10.12%** | Correct entity present in Top 5, but displaced by adjacent locality or parent district. |
| **Category D** | `CORRECT_RETRIEVED_RANK_6_10` | **0** | **0.00%** | When retrieved, entities are concentrated in Top 5. |
| **Category E** | `CORRECT_RETRIEVED_RANK_GT10` | **0** | **0.00%** | No deep tail dropouts. |
| **Category A** | `CORRECT_NOT_IN_UNIVERSE` | **584** | **11.68%** | Rural villages / remote subdistricts not present in reference gazetteer. |
| **Category F** | `GROUND_TRUTH_SCHEMA_MISMATCH`| **0** | **0.00%** | Schema alignment validated. |
| **Category G** | `DECISION_LAYER_FAILURE` | **0** | **0.00%** | Downstream verification decision engine operates deterministically. |
| **Total** | Full Independent Benchmark | **5,000** | **100.00%** | Cumulative Candidate Recall@5: **88.32%** |

---

## 3. Key Takeaways
1. **High Retrieval Ceiling**: For **88.32%** of all independent cases across 36 States/UTs, the correct geographic entity is retrieved within the top 5 candidate slots.
2. **Ranking Displacements (506 Cases / 10.12%)**: The dominant displacement occurs between Locality vs Parent District or between adjacent postal sub-offices sharing a PIN circle.
3. **Unindexed Rural Long-Tail (584 Cases / 11.68%)**: Represents the remaining unindexed rural settlements in remote or tribal regions where local village names are not yet present in national gazetteer catalogs. GeoVerify correctly handles these cases conservatively with `CONSISTENT` (partial) or `NEEDS_REVIEW` rather than false positive `VERIFIED`.
