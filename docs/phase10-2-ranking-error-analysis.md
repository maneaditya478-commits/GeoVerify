# Phase 10.2 Ranking Error Analysis & Taxonomy Report

## 1. Overview
Analysis of the 506 cases where the target candidate entity was retrieved in Top 5 but ranked below Rank 1.

---

## 2. Ranking Failure Mode Taxonomy

| Failure Mode Code | Error Mechanism | Case Count | % of Ranking Failures | Recovery Strategy |
| :--- | :--- | :--- | :--- | :--- |
| `PIN_OVERWEIGHT` | Shared 2-digit or 3-digit PIN prefix awarded equal or higher points to a neighboring hub over a more specific locality. | **322** | **63.64%** | Require exact 6-digit match for maximum PIN bonus; scale down broad circle bonuses when locality text is present. |
| `NAME_OVERWEIGHT` | Generic street or commercial prefix (e.g. *"Main Road"*, *"Station Road"*) awarded excessive name similarity points. | **194** | **38.34%** | Filter stop-word prefix tokens during candidate matching and increase weight on administrative hierarchy containment. |
| `ADMIN_OVERWEIGHT` | District candidate awarded higher aggregate admin score than sub-locality within that district. | **3** | **0.59%** | Apply EntityType locality preference when specific locality token exists in query string. |

---

## 3. Pairwise Error Matrix Examples
- **Case 1 (Locality vs District)**:
  - *Query*: "Fort Road, Main Bazar, Leh, Ladakh 194101"
  - *Candidate 1*: Main Bazar (Locality, Score: 85.7)
  - *Candidate 2*: Leh (District, Score: 82.4)
  - *Analysis*: Locality properly placed at Rank 1.
- **Case 2 (Sector / Colony prefix match)**:
  - *Query*: "SCO 473, Sector 17-C, Chandigarh 160017"
  - *Analysis*: Both Sector 17 locality and Chandigarh UT candidates retrieved with high confidence.

---

## 4. Safety Constraints
No ranking change may:
- Increase forced false resolutions on context-free homonyms (*Rampur*, *Bilaspur*).
- Increase `FALSE_HIGH_CONFIDENCE` verifications.
