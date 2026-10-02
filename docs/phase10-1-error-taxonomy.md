# GeoVerify India — Phase 10.1: Error Taxonomy & Root Cause Classification

## 1. Taxonomic Classification Structure

GeoVerify assigns every failed verification to exactly one mutually exclusive primary root cause:

| Error Code | Category | Severity Level (1-5) | Description & Invariant |
| :--- | :--- | :--- | :--- |
| **`SEVERE_OCR`** | OCR Degradation | 4 (High) | Severe character corruption / token loss in OCR text preventing parsing. |
| **`CONTEXT_FREE_HOMONYM`**| Ambiguity | 1 (Safe) | Locality name exists in multiple districts; correctly flagged `AMBIGUOUS`. |
| **`JURISDICTION_MISMATCH`**| Administrative Conflict | 1 (Safe) | Genuine geographic clash between stated state/district/locality; flagged `INCONSISTENT`.|
| **`DRAVIDIAN_PHONETIC_ERROR`**| Multilingual | 3 (Moderate) | Transliteration variant in Tamil/Telugu/Kannada not resolved to canonical name. |
| **`TRIBAL_GAZETTEER_GAP`** | Gazetteer Coverage | 3 (Moderate) | Remote village/hamlet not present in Level-4 in-memory gazetteer. |
| **`BENGALI_ASSAMESE_ALIGNMENT`**| Multilingual | 3 (Moderate) | Bengali/Assamese script tokenization or compound character split failure. |
| **`MISSING_EVIDENCE`** | Incompleteness | 2 (Low) | Essential administrative levels omitted by user; flagged `NEEDS_REVIEW` or `AMBIGUOUS`. |
| **`CORRECT_NOT_RETRIEVED`**| Retrieval Deficit | 4 (High) | Target entity was not retrieved into the top-10 candidate pool. |
| **`CORRECT_RETRIEVED_MIS_RANKED`**| Ranking Deficit | 3 (Moderate) | Target entity was in candidate pool but outranked by irrelevant candidate. |
| **`TEMPORAL_ERROR`** | Temporal Reasoning | 2 (Low) | Reference query date misinterpreted or historical transition boundary error. |
| **`LANDMARK_ERROR`** | Spatial Proximity | 2 (Low) | Landmark coordinates outside stated buffer radius. |
| **`FALSE_HIGH_CONFIDENCE`**| Safety Critical | 5 (Critical) | High confidence ($>0.80$) asserted on geographically incorrect decision (Invariant: **0 occurrences**).|
