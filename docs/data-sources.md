# Authoritative Data Sources & Reference Datasets

GeoVerify India relies exclusively on authoritative, open-government, and open-source geospatial datasets. No synthetic or fabricated geographic coordinates are used.

---

## 1. Primary Sources & Registry

| Dataset / Authority | Coverage | License | Update Cadence | Key Identifiers |
| :--- | :--- | :--- | :--- | :--- |
| **Local Government Directory (LGD)**<br>`https://lgdirectory.gov.in/` | 36 States & UTs, 750+ Districts, Sub-Districts (Talukas / Tehsils / Mandals) | GODL-India | Monthly / Quarterly | LGD State Code, LGD District Code, LGD Sub-District Code |
| **Survey of India (SOI)**<br>`https://surveyofindia.gov.in/` | Authoritative National, State & District Boundary Polygons | GODL-India | Annual | National Boundaries, Coastal Line |
| **India Post (Department of Posts)**<br>`https://data.gov.in/resource/all-india-pincode-directory` | All-India 6-Digit PIN Code Postal Directory & Post Offices | GODL-India | Bi-annual | 6-Digit PIN, Circle Code, Delivery Division |
| **OpenStreetMap (OSM) India Contributors**<br>`https://www.openstreetmap.org/` | Urban Localities, Points of Interest, Major Transit Hubs, Commercial Centers | ODbL (Open Database License) | Continuous / Weekly | OSM Node/Way/Relation ID |

---

## 2. Licensing Compliance

- **Government Open Data License (GODL-India):**
  - Allows public access, processing, and derivative work publication.
  - Attribution given to the respective Ministries (Ministry of Panchayati Raj, Ministry of Communications, Ministry of Science and Technology).
- **Open Database License (ODbL):**
  - OpenStreetMap contributors attribution maintained in all verification responses and user interface views.

---

## 3. Dataset Update & Ingestion Pipeline

All authoritative datasets are processed and maintained via automated scripts:

```powershell
# 1. Fetch source manifests and generate staging checksums
.\backend\.venv\Scripts\python data/scripts/download/fetch_sources.py

# 2. Transform into canonical JSON/GeoJSON with multilingual aliases
.\backend\.venv\Scripts\python data/scripts/transform/transform_admin_data.py

# 3. Validate geometry and hierarchy integrity
.\backend\.venv\Scripts\python data/scripts/validate/validate_geography.py

# 4. Ingest into PostGIS / relational database
.\backend\.venv\Scripts\python data/scripts/import/import_postgis.py
```
