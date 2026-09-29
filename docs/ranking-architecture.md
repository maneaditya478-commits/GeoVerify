# GeoVerify India — Phase 6 Context-Aware Candidate Ranking Architecture

## 1. Overview & Objective

The **GeoVerify India Context-Aware Candidate Ranking Engine** (`backend/app/entity_resolution/ranking.py`) transforms multi-channel geographic candidate pools into accurate, explainable, and calibrated entity resolution rankings.

In Phase 5, multi-channel candidate generation (Exact, Alias, Transliteration, Indic Phonetic, Fuzzy, Admin-Context, PIN-Constrained, Spatial BBox) achieved a top-5 candidate recall of **98.74%**. However, ranking diagnosis revealed that without explicit administrative penalties and parent-child multi-tier consistency checks, correct candidates in the Top-5 pool were occasionally outranked by cross-state homonyms or district entities matching raw locality strings.

Phase 6 implements a **9-factor context-aware scoring model** combined with **explicit administrative conflict penalties** and **explainable ranking rationales**.

---

## 2. Multi-Factor Scoring Architecture

Candidate entities are evaluated across nine distinct geographic and textual signals:

| Component | Weight | Max Points | Description |
|---|---|---|---|
| **Name Similarity** | 25% | 25.0 pts | Exact matching, historical/colloquial aliases, NFC normalized text, and length-adaptive fuzzy similarity. |
| **Administrative Context** | 25% | 25.0 pts | Direct agreement with extracted parent State, District, and Sub-district/Taluka tokens. |
| **Parent-Child Compatibility** | 15% | 15.0 pts | Verified hierarchical consistency in Local Government Directory (LGD) authoritative database. |
| **PIN Compatibility** | 10% | 10.0 pts | Exact 6-digit PIN match (10.0 pts), 3-digit postal circle match (7.0 pts), or 1-digit postal zone match (4.0 pts). |
| **Geographic Proximity** | 10% | 10.0 pts | Haversine distance ($\le 5\text{ km} \rightarrow 10.0\text{ pts}$, $\le 15\text{ km} \rightarrow 8.0\text{ pts}$, $\le 50\text{ km} \rightarrow 4.0\text{ pts}$) or bounding box containment. |
| **Transliteration & Phonetics** | 5% | 5.0 pts | Devanagari script transliteration match and Indic phonetic (Soundex/Metaphone) agreement. |
| **Entity Type Compatibility** | 5% | 5.0 pts | Target entity classification alignment (Locality, Village, Town, POI vs District vs State). |
| **Retrieval Consensus Bonus** | 3% | 3.0 pts | Bonus for candidates retrieved independently across multiple channels ($\ge 3\text{ channels} \rightarrow 3.0\text{ pts}$, $2\text{ channels} \rightarrow 2.0\text{ pts}$). |
| **Data Quality & Authority** | 2% | 2.0 pts | Source authority (LGD / SOI / India Post) and completeness of coordinate and bounding box geometries. |
| **Total Positive Score** | **100%** | **100.0 pts** | Sum of all positive feature contributions. |

---

## 3. Explicit Administrative Conflict Penalties

When a candidate entity contradicts an asserted or verified geographic context, explicit penalty deductions are subtracted from the raw score:

```text
Final Score = clamp(Positive Feature Sum + Sum of Applied Penalties, 0.0, 100.0)
```

| Penalty Identifier | Deduction | Trigger Condition | Rationale |
|---|---|---|---|
| `STATE_CONFLICT` | **-40.0 pts** | Candidate state contradicts asserted state. | Eliminates cross-state homonyms (e.g. Rampur UP vs Rampur Bihar) when state is known. |
| `DISTRICT_CONFLICT` | **-25.0 pts** | Candidate district contradicts asserted district. | Prevents intra-state homonyms in wrong districts from outranking the correct locality. |
| `ENTITY_TYPE_MISMATCH` | **-30.0 pts** | Candidate is District/State when query searches for Locality. | Stops district entities from outranking localities with identical names (e.g. Pune district vs Pune city locality). |
| `PIN_CIRCLE_CONFLICT` | **-20.0 pts** | Candidate PIN postal circle contradicts query PIN code. | Penalizes candidates whose postal circle is in a different geographic zone. |
| `SUBDISTRICT_CONFLICT` | **-15.0 pts** | Candidate subdistrict contradicts asserted Taluka/Tehsil. | Distinguishes localities across sub-districts within the same district. |

---

## 4. Explainable Ranking Output

Every candidate evaluation produces a structured `RankingExplanation`:

```json
{
  "feature_contributions": {
    "name_similarity": 25.0,
    "admin_context": 25.0,
    "parent_child_compatibility": 15.0,
    "pin_compatibility": 10.0,
    "geographic_proximity": 10.0,
    "transliteration_phonetic": 3.0,
    "entity_type_weight": 5.0,
    "retrieval_consensus": 3.0,
    "data_quality": 2.0,
    "penalty_deduction": 0.0
  },
  "applied_penalties": [],
  "retrieval_channels": ["exact", "alias", "admin_context"],
  "consensus_count": 3,
  "rank": 1,
  "score_delta_to_next": 14.5,
  "admin_differences": [],
  "summary": "Rank #1 (98.0/100). Lead over Rank #2: +14.5 pts. Found via 3 channel(s)."
}
```

---

## 5. Confidence Bands

Candidate match confidence is deterministically mapped based on calibrated score thresholds:

- **HIGH Confidence:** $\text{Score} \ge 85.0$
- **MEDIUM Confidence:** $65.0 \le \text{Score} < 85.0$
- **LOW Confidence:** $\text{Score} < 65.0$
