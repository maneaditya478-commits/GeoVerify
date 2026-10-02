# Phase 10.2 Ranking Model Audit & Architecture Reference

## 1. Overview
Candidate ranking in GeoVerify India is governed by the `ContextAwareRanker` (`backend/app/entity_resolution/ranking.py`) and `Phase6RankingConfig` (`backend/app/entity_resolution/ranking_config.py`).

The scoring model is a transparent, deterministic multi-factor additive model with applied administrative penalties and retrieval consensus bonuses.

---

## 2. Feature Contributions & Weighting Breakdown

| Factor | Baseline Weight | Maximum Points | Description |
| :--- | :--- | :--- | :--- |
| **Name Similarity** | 25% | 25.0 | Token-level fuzzy and exact name similarity across Latin, Devanagari, and Indic aliases. |
| **Admin Context Agreement** | 25% | 25.0 | Proportional match across State, District, and Subdistrict context provided in query. |
| **Parent-Child Compatibility** | 15% | 15.0 | Hierarchical containment verified through `HierarchyValidator` and spatial bounding boxes. |
| **PIN Compatibility** | 10% | 10.0 | Postal circle, 3-digit prefix, and exact 6-digit match against `pincodes.json`. |
| **Geographic Proximity** | 10% | 10.0 | Great-circle Haversine distance (<5km: 10pts, <15km: 8pts, <50km: 4pts). |
| **Transliteration / Phonetic** | 5% | 5.0 | Pan-Indic phonetic token matching and Indic script normalization. |
| **Entity Type Weight** | 5% | 5.0 | Priority given to expected entity level (Locality vs District vs Subdistrict). |
| **Retrieval Consensus** | 3% | 3.0 | Bonus for candidates returned independently across multiple retrieval channels (exact, dense, spatial). |
| **Data Quality** | 2% | 2.0 | Provenance bonus for authoritative LGD / Survey of India records. |

---

## 3. Explicit Administrative Penalties

| Penalty Rule | Deduction | Trigger Condition |
| :--- | :--- | :--- |
| `STATE_CONFLICT` | **-40.0 pts** | Candidate state explicitly contradicts query-asserted state. |
| `DISTRICT_CONFLICT` | **-25.0 pts** | Candidate district explicitly contradicts query-asserted district. |
| `SUBDISTRICT_CONFLICT` | **-15.0 pts** | Candidate subdistrict contradicts asserted taluka/mandal. |
| `PIN_CIRCLE_CONFLICT` | **-20.0 pts** | Candidate PIN 2-digit postal circle contradicts asserted PIN code. |

---

## 4. Ambiguity Resolution & Threshold Semantics
- **Ambiguity Margin**: If the top two candidates have a score margin $\le 10.0$ points and both represent distinct jurisdictions without sufficient context to disambiguate, `AmbiguityDetector` flags `is_ambiguous = True` and transitions status to `AMBIGUOUS`.
- **Conservative Decision Engine**: Low-scoring entities (<55.0) are never forced into `VERIFIED`, preventing manufactured confidence.
