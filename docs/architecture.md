# GeoVerify India Architecture (Phase 2)

## 1. System Overview

GeoVerify India is a multi-signal geospatial and administrative consistency verification platform designed specifically for the complexities of Indian addresses.

```mermaid
flowchart TD
    User([User / API Client]) -->|Submit Address| API[FastAPI Gateway]
    
    subgraph IngestionPipeline [Authoritative Data Pipeline]
        LGD["LGD (Gov of India)"] --> Download["data/scripts/download/"]
        SOI["Survey of India"] --> Download
        IP["India Post"] --> Download
        OSM["OpenStreetMap"] --> Download
        Download --> Staging["data/staging/ (Manifest & SHA-256)"]
        Staging --> Validation["data/scripts/validate/ (Shapely)"]
        Validation --> Transform["data/scripts/transform/ (Multilingual)"]
        Transform --> Processed["data/processed/ (JSON / GeoJSON)"]
        Processed --> PostGIS["PostGIS / SQLAlchemy (EPSG:4326)"]
    end

    subgraph VerificationPipeline [Verification Pipeline]
        API --> Norm[1. Address Normalizer (Aliases & Devanagari)]
        Norm --> Parse[2. Structured Parser (Premise, Taluka, Pin)]
        Parse --> Geo[3. Geocoding Provider Layer]
        
        Geo --> Hier["4. Multi-Tier Hierarchy (Country ➔ State ➔ District ➔ Taluka ➔ Locality)"]
        Geo --> Bound["5. Point-in-Polygon Boundaries (State, District, Taluka)"]
        Geo --> Pin["6. PIN Code Validator (Format, Circle, Centroid Distance)"]
        Geo --> Near["7. Nearby Context (Transit, Hospitals, POIs)"]
        
        Hier --> Evid[8. Evidence & Explainability Engine]
        Bound --> Evid
        Pin --> Evid
        Near --> Evid
        
        Evid --> Score[9. Geographic Consistency Scoring (0 - 100)]
    end
    
    PostGIS -.-> Hier
    PostGIS -.-> Bound
    PostGIS -.-> Pin
    PostGIS -.-> Near
    
    Score --> Result[Verification Response + GeoJSON + Data Sources]
    Result --> Frontend[React / Vite / Leaflet GIS UI]
```

---

## 2. Component Architecture

### 2.1 Address Normalization Pipeline (`app/services/normalizer.py`)
- Standardizes capitalization, whitespace, and punctuation.
- Resolves abbreviations (e.g., `Rd` ➔ `Road`, `Bhd` ➔ `Behind`, `Sec` ➔ `Sector`).
- Normalizes state names across English, Hindi (`महाराष्ट्र`, `कर्नाटक`, `दिल्ली`), and Marathi aliases.
- Normalizes district aliases (`Poona` ➔ `Pune`, `Bombay` ➔ `Mumbai Suburban`, `Calcutta` ➔ `Kolkata`, `Madras` ➔ `Chennai`).
- Formats 6-digit Indian PIN codes.
- Maintains a full `TransformationStep` audit trail.

### 2.2 Structured Parser (`app/services/address_parser.py`)
- Deconstructs free-form address strings into:
  - Premise / Building / Flat / Plot
  - Locality / Village (English & Devanagari)
  - Sub-district / Taluka / Tehsil (`Haveli`, `Mulshi`, `Chanakyapuri`, `Alipore`)
  - District / City
  - State & State Code
  - PIN Code
  - Landmarks (`Near EON IT Park`, `Opposite Inorbit Mall`)

### 2.3 Geocoding Provider Layer (`app/services/geocoder.py`)
- Abstract interface `GeocoderProvider`.
- `MockGeocoder`: High-fidelity offline reference dataset with fuzzy matching for development and testing.
- `NominatimGeocoder`: OpenStreetMap live geocoding provider with rate-limiting and fallback.
- In-memory caching layer.

### 2.4 Administrative Hierarchy Engine (`app/verification/hierarchy.py`)
- Enforces multi-tier Indian administrative structure:
  $$\text{Country} \rightarrow \text{State} \rightarrow \text{District} \rightarrow \text{Sub-District (Taluka/Tehsil)} \rightarrow \text{Locality}$$
- Detects administrative conflicts (e.g. `Kharadi` placed under `Kolhapur` instead of `Pune`).

### 2.5 Point-in-Polygon Boundary Verification (`app/verification/boundaries.py`)
- Uses Shapely geometries (`Polygon.contains(Point)`).
- Verifies geometric containment within state, district, and subdistrict polygons.
- Emits GeoJSON FeatureCollection layers for Leaflet map rendering.

### 2.6 PIN Code Verification (`app/services/pin_validator.py`)
- Separated validation breakdown:
  1. 6-digit numeric format validation.
  2. Postal circle prefix consistency check (e.g., `4` for Maharashtra/Goa, `5` for Karnataka/Andhra).
  3. Postal district cross-referencing.
  4. Centroid spatial distance calculation via Haversine formula.

### 2.7 Nearby Intelligence Service (`app/services/nearby.py`)
- Identifies contextual amenities (transit hubs, hospitals, police stations, IT parks, post offices) within a configurable radius (e.g., 5 km).

### 2.8 Geographic Directory API (`app/api/routes/geography.py`)
- `GET /api/geography/states`: All 36 States and UTs with LGD codes and multilingual names.
- `GET /api/geography/districts?state_code=MH`: Filtered district catalog.
- `GET /api/geography/subdistricts?district_id=dist_pune`: Sub-districts / talukas.
- `GET /api/geography/pincode/{pincode}`: Authoritative PIN code centroid and circle details.
- `GET /api/geography/search?q=...`: Multilingual search across all administrative tiers.
