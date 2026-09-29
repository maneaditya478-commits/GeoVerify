# Authoritative Data Sources & Reference Datasets

GeoVerify India relies on authoritative and open geographic datasets for Indian administrative boundaries and postal directories.

## 1. Primary Sources

1. **Local Government Directory (LGD) - Ministry of Panchayati Raj, Government of India**
   - Standard administrative hierarchy (State, District, Sub-district, Village/Local Body codes).
   - Website: https://lgdirectory.gov.in/

2. **Survey of India (SOI)**
   - Official administrative boundary shapefiles and national cartographic standards.
   - Website: https://surveyofindia.gov.in/

3. **India Post (Department of Posts)**
   - All-India PIN Code directory with Postal Circles, Regions, Divisions, and Post Office names.
   - Website: https://data.gov.in/resource/all-india-pincode-directory

4. **OpenStreetMap (OSM) & Nominatim**
   - Community-maintained points of interest, transit stations, and road infrastructure.
   - License: Open Database License (ODbL).

---

## 2. Ingestion Strategy

All reference datasets are processed and stored under `data/processed/` in standard GeoJSON / JSON format.

To regenerate local seed datasets:
```bash
python data/scripts/generate_seed_data.py
```
