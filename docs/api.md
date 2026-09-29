# GeoVerify India REST API Documentation

The GeoVerify API provides REST endpoints for address parsing, transliteration, candidate entity resolution, ambiguity detection, completeness scoring, directed evidence graph generation, and multi-signal consistency verification.

## Base URL
`http://localhost:8000/api`

Interactive Swagger Docs: `http://localhost:8000/docs`

---

## 1. Verify Address

**`POST /api/verify`**

Execute complete multi-signal geographic consistency verification and returns multi-scores, ambiguity details, candidate matches, and the directed evidence graph.

### Request Body (Free-Form):
```json
{
  "address": "Kharadi, Pune, Maharashtra 411014",
  "radius_km": 5.0,
  "include_geojson": true
}
```

### Request Body (Structured):
```json
{
  "structured": {
    "address_line": "Flat 402, Ganga Carnation, Near EON IT Park",
    "locality": "Kharadi",
    "subdistrict": "Haveli",
    "district": "Pune",
    "state": "Maharashtra",
    "pincode": "411014"
  },
  "radius_km": 5.0,
  "include_geojson": true
}
```

### Response (`200 OK`):
```json
{
  "verification_id": "gv_948fbc2014ea",
  "timestamp": "2026-09-29T12:00:00Z",
  "status": "VERIFIED",
  "score": 94,
  "scores": {
    "geographic_consistency": 94,
    "address_completeness": 90,
    "entity_match": 95
  },
  "summary": "Strong geographic, administrative, and geometric consistency verified across all signals.",
  "explanation": [
    "✓ State 'Maharashtra' exists in official LGD registry",
    "✓ District 'Pune' belongs to Maharashtra",
    "✓ Sub-District 'Haveli' is an authoritative taluka of Pune",
    "✓ Locality 'Kharadi' belongs to Haveli taluka",
    "✓ Coordinates fall within expected district polygon (Pune)",
    "✓ PIN code '411014' belongs to Maharashtra Postal Circle 4"
  ],
  "warnings": [],
  "evidence_graph": {
    "nodes": [...],
    "relationships": [...],
    "summary": "Administrative hierarchy is fully consistent.",
    "conflicts_count": 0,
    "warnings_count": 0
  }
}
```

---

## 2. Address Entity Resolution

**`POST /api/address/resolve`**

Resolves all address components against the administrative gazetteer with multi-factor match scoring and ambiguity evaluation.

### Request Body:
```json
{
  "address": "World Trade Center, Kharadi, Pune, Maharashtra 411014"
}
```

---

## 3. Geographic Candidate Search

**`GET /api/address/candidates?q=Kharadi&state=Maharashtra&limit=10`**

Retrieves ranked candidates for a given query token with exact, alias, and fuzzy phonetic matching.

---

## 4. Ambiguity Detection

**`POST /api/address/ambiguity`**

Evaluates address tokens for homonymous multi-location ambiguity and provides required disambiguation fields.

### Request Body:
```json
{
  "address": "Bilaspur"
}
```

### Response:
```json
{
  "is_ambiguous": true,
  "top_candidates": [
    { "candidate": { "name": "Bilaspur", "state": "Chhattisgarh", "entity_type": "district" }, "match_score": 85 },
    { "candidate": { "name": "Bilaspur", "state": "Himachal Pradesh", "entity_type": "district" }, "match_score": 85 }
  ],
  "ambiguity_reason": "Address 'Bilaspur' matches multiple distinct locations across different jurisdictions.",
  "suggested_disambiguations": [
    "State name (e.g., 'Chhattisgarh', 'Himachal Pradesh')",
    "PIN code"
  ]
}
```

---

## 5. Address Completeness Scoring

**`POST /api/address/completeness`**

Evaluates structural completeness of an address across 6 weighted administrative dimensions.

### Request Body:
```json
{
  "address": "Kharadi, Pune, Maharashtra 411014"
}
```

### Response:
```json
{
  "score": 90,
  "rating": "COMPLETE",
  "missing_fields": [],
  "breakdown": {
    "state": 25.0,
    "district": 25.0,
    "locality": 20.0,
    "pincode": 15.0,
    "premise": 5.0,
    "landmark": 0.0
  }
}
```

---

## 6. Retrieve Directed Evidence Graph

**`GET /api/evidence/{verification_id}`**

Retrieves the structured Directed Evidence Graph nodes, edges, severity badges, and summary for a past verification.

---

## 7. Address Normalization & Transliteration

**`POST /api/address/normalize`**

```json
{
  "address_line": "Near EON Free Zone, Kharadi",
  "city": "पुणे",
  "state": "महाराष्ट्र",
  "pincode": "411014"
}
```

---

## 8. Address Parsing

**`POST /api/address/parse`**

Supports Devanagari prefix extraction (`गाव:`, `तालुका:`, `जिल्हा:`, `राज्य:`, `पिन:`) and free-form parsing.
