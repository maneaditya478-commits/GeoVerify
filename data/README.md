# GeoVerify India Reference Datasets

This directory contains reference datasets and ingestion scripts for Indian administrative units, postal codes, and landmarks.

## Structure

- `raw/`: Raw downloaded shapefiles and government datasets (ignored by git).
- `processed/`: Curated JSON / GeoJSON boundary files used by the verification engine and offline geocoder.
- `scripts/`: Python scripts for generating seed data and transforming source datasets.

## Seed Data Generation

To generate the reference files in `processed/`:
```bash
python data/scripts/generate_seed_data.py
```
