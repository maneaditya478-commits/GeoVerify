# GeoVerify India — Phase 10.1: Retrieval Gap Analysis & Channel Provenance

## 1. Executive Summary

In Phase 10, Candidate Recall@1 was 15.74% and Recall@5 was 25.00%. This audit investigates why candidate generation failed and redesigns the multi-channel candidate retrieval architecture with explicit provenance tracking.

---

## 2. Multi-Channel Retrieval Taxonomy & Diagnostic Audit

GeoVerify generates candidates through 10 distinct channels:
1. `EXACT`: Canonical lowercase string equality on name and aliases.
2. `ALIAS`: Known historical, colloquial, and administrative acronym mappings.
3. `TRANSLITERATION`: Indic script conversion to Latin canonicals.
4. `PHONETIC`: Indian place-name phonetic hashing and consonant-group invariant matching.
5. `FUZZY`: Length-adaptive bounded Levenshtein/token sort ratio ($\ge 75\%$).
6. `ADMIN_CONTEXT`: Hierarchy-aware candidate scoping constrained by parsed parent district/state.
7. `PIN`: Spatial matching constrained to postal delivery zones.
8. `SPATIAL`: Point-in-polygon and KD-tree nearest-neighbour search within radius.
9. `DENSE`: Dense char-ngram embedding similarity for occluded/noisy tokens.
10. `GRAPH`: Subgraph neighbor discovery from connected entity nodes.

---

## 3. Channel Attribution & Gap Decomposition

| Retrieval Channel | Hits in Phase 9 (4 States) | Hits in Phase 10 (36 States) | Gap Cause | Phase 10.1 Target Capability |
| :--- | :--- | :--- | :--- | :--- |
| **Exact** | 42.5% | 8.2% | Unindexed districts/localities | National 780+ district coverage |
| **Alias / Historic** | 12.0% | 2.1% | Regional aliases limited to MH/KA | Comprehensive all-state aliases |
| **Transliteration** | 18.5% | 1.8% | Devanagari only | Pan-Indic (Tamil, Telugu, Kannada, Bengali, Odia, Gujarati) |
| **Phonetic** | 11.2% | 1.5% | Dravidian consonant clusters unhandled | Enhanced South/East Indian phonetic rules |
| **Admin Context** | 8.0% | 1.2% | Parent district lookup failed | Complete State $\to$ District $\to$ Taluka trees |
| **Dense / N-Gram** | 4.0% | 0.9% | Missing dictionary tokens | Re-indexed national vocabulary |

---

## 4. Retrieval Provenance & Explainability Invariant

In Phase 10.1, every candidate entity emitted by `MultiStageCandidateGenerator` must retain its full retrieval provenance:
```python
candidate.provenance_channels = ["EXACT", "ADMIN_CONTEXT"]
candidate.retrieval_score = 0.95
```
A candidate must **never** be injected from an unexplained or hidden heuristic.
