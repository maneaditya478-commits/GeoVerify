# GeoVerify India REST API Documentation

The GeoVerify API provides REST endpoints for address parsing, normalization, geocoding, and multi-signal consistency verification.

## Base URL
`http://localhost:8000/api`

Interactive Swagger Docs: `http://localhost:8000/docs`

---

## 1. Verify Address

**`POST /api/verify`**

Execute complete multi-signal geographic consistency verification.

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
  "summary": "Strong geographic, administrative, and geometric consistency verified across all signals.",
  "explanation": [
    "✓ State 'Maharashtra' exists",
    "✓ District 'Pune' belongs to Maharashtra",
    "✓ Coordinates fall within expected district (Pune)",
    "✓ Locality 'Kharadi' identified and consistent",
    "✓ PIN code '411014' is consistent with postal circle and region",
    "✓ Found 8 contextual geographic landmarks nearby"
  ],
  "warnings": [],
  "score_breakdown": {
    "hierarchy_score": 25.0,
    "hierarchy_max": 25.0,
    "boundary_score": 25.0,
    "boundary_max": 25.0,
    "locality_score": 20.0,
    "locality_max": 20.0,
    "pincode_score": 15.0,
    "pincode_max": 15.0,
    "geocoding_score": 9.5,
    "geocoding_max": 10.0,
    "nearby_score": 5.0,
    "nearby_max": 5.0,
    "total_score": 94
  },
  "geocoding": {
    "coordinates": {
      "latitude": 18.5514,
      "longitude": 73.9405
    },
    "display_name": "Kharadi, Pune, Maharashtra",
    "source": "Local Reference Catalog",
    "confidence": 0.95
  },
  "administrative_hierarchy": {
    "country": "India",
    "state": "Maharashtra",
    "district": "Pune",
    "locality": "Kharadi",
    "is_consistent": true
  }
}
```

---

## 2. Address Normalization

**`POST /api/address/normalize`**

```json
{
  "address_line": "Near EON Free Zone, Kharadi",
  "city": "Poona",
  "state": "Maharastra",
  "pincode": "411 014"
}
```

---

## 3. Address Parsing

**`POST /api/address/parse`**

```json
{
  "address": "Flat 402, Ganga Carnation, Near EON IT Park, Kharadi, Pune, Maharashtra 411014"
}
```

---

## 4. Nearby Intelligence

**`GET /api/nearby?latitude=18.5514&longitude=73.9405&radius_km=5.0`**

---

## 5. Verification History

**`GET /api/address/history?limit=20`**
