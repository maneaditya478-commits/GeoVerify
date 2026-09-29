# GeoVerify India Evaluation Datasets

This directory stores reproducible address intelligence benchmark datasets for GeoVerify India.

## Files

* `benchmark.json`: Master JSON dataset containing 1,000+ structured test cases with independent ground-truth annotations across 19 categories and multiple Indic scripts.
* `benchmark.csv`: Tabular export of the benchmark dataset.

## Provenance & Privacy

* All entities are synthesized from official government gazetteers (Local Government Directory and Department of Posts) or publicly documented geographic landmarks.
* **No personal identifying information (PII) or private resident addresses are included.**
* All records are labeled with `source_type`: `PUBLIC`, `SYNTHETIC`, or `DERIVED`.
