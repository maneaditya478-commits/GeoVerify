# GeoVerify India 🇮🇳

[![CI](https://github.com/maneaditya478-commits/GeoVerify/actions/workflows/ci.yml/badge.svg)](https://github.com/maneaditya478-commits/GeoVerify/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![React: 18](https://img.shields.io/badge/React-18-cyan.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-teal.svg)](https://fastapi.tiangolo.com/)
[![Tests: 112 Passing](https://img.shields.io/badge/Pytest-112%20Passing-brightgreen.svg)](backend/tests)
[![Candidate Recall@5: 98.7%](https://img.shields.io/badge/Recall%405-98.74%25-blueviolet.svg)](docs/candidate-retrieval-architecture.md)
[![Benchmark: 1,065 Cases](https://img.shields.io/badge/Benchmark-1%2C065%20Cases-purple.svg)](evaluation/)

**GeoVerify India** is an open-source address intelligence, entity resolution, and geographic consistency verification platform tailored for the unique administrative and spatial complexities of Indian addresses.

---

## 1. Problem Statement

Indian addresses are characterized by diverse informal formatting, colloquial locality names, transliteration variations in regional scripts (Hindi, Marathi), municipal ward reorganizations, and multi-tier administrative subdivisions (Tehsils, Talukas, Postal Circles).

Traditional address verification systems suffer from:
* **Binary "fake or real" false positives** due to simple spelling variations or abbreviations (`Maharastra` vs `Maharashtra`, `BLR` vs `Bengaluru`, `महाराष्ट्र` vs `Maharashtra`).
* **Silent geocoding errors** where an address in one district is placed in another without administrative validation.
* **Low Candidate Recall** where colloquial or phonetically mangled place names fail to enter the candidate pool.
* **Lack of explainability**, providing black-box confidence scores without actionable evidence.
* **Homonymous geographic confusion** between identically named towns across different states (e.g., *Bilaspur* in Chhattisgarh vs Himachal Pradesh, *Rampur* across multiple states).

---

## 2. What GeoVerify Can vs Cannot Establish

### What GeoVerify Can Establish:
* Authoritative administrative consistency between Locality, Sub-District (Taluka), District, State, and PIN code.
* Whether an asserted geographic entity exists in official Indian registries (Local Government Directory and India Post).
* Geometric point-in-polygon containment against official state and district boundaries.
* Homonymous ambiguities and specific required fields needed for disambiguation.
* Structural address completeness across 6 administrative dimensions.

### What GeoVerify Cannot Establish:
* Physical presence or residency of a specific individual or business at an address.
* Deliverability of mail inside private apartment gates or internal unit numbers.
* Ownership or legal title of private properties.

---

## 3. Architecture & Multi-Score Pipeline

```mermaid
flowchart TD
    Input["Input: 'गाव: खराडी, तालुका: हवेली, जिल्हा: पुणे, 411014'"] --> Indic[1. Indic Script Detection & Transliteration]
    Indic --> EntityRes[2. Multi-Stage Candidate Generation (9 Channels)]
    EntityRes --> ReRank[3. Context-Aware Re-Ranking]
    ReRank --> Ambiguity{4. Ambiguity Check}
    
    subgraph MultiSignal [Multi-Signal Verification Engine]
        ReRank --> Hier["5. Multi-Tier Hierarchy (25 pts)"]
        ReRank --> Bound["6. Point-in-Polygon Boundaries (25 pts)"]
        ReRank --> Loc["7. Locality Match (20 pts)"]
        ReRank --> Pin["8. PIN Code Validation (15 pts)"]
        ReRank --> Geoc["9. Geocoding Quality (10 pts)"]
        ReRank --> Near["10. Nearby Context (5 pts)"]
    end
    
    MultiSignal --> EvidGraph["11. Directed Evidence Graph Builder"]
    EvidGraph --> MultiScores["12. Multi-Score Evaluation"]
    
    MultiScores --> S1["Geographic Consistency (0-100)"]
    MultiScores --> S2["Address Completeness (0-100)"]
    MultiScores --> S3["Entity Match Score (0-100)"]
```

---

## 4. Key Features (Phase 5)

- **Multi-Stage Independent Candidate Retrieval (9 Channels)**: Exact, Structured Alias, Suffix-Normalized, Indic Transliteration, Indian Phonetic (Indic-Soundex), Length-Adaptive Fuzzy, Administrative Context-Guided, PIN-Constrained, and Spatial Bounding Box.
- **High Candidate Recall Ceiling**: Empirically achieves **98.74% Recall@5** and **76.23% Recall@1** on the 1,065-case benchmark.
- **Indian Place-Name Phonetic Matching**: Robust tolerance for phonetic variations (`Puna` $\rightarrow$ `Pune`, `Nasik` $\rightarrow$ `Nashik`, `Ahemadnagar` $\rightarrow$ `Ahmednagar`, `Khardi` $\rightarrow$ `Kharadi`).
- **Structured External Alias Catalog**: Data-driven historical and colloquial aliases (`Poona` $\rightarrow$ `Pune`, `Bombay` $\rightarrow$ `Mumbai`, `Calcutta` $\rightarrow$ `Kolkata`, `Madras` $\rightarrow$ `Chennai`, `CP` $\rightarrow$ `Connaught Place`).
- **Deterministic Multi-Score Engine**: Computes Geographic Consistency Score ($0-100$), Address Completeness Score ($0-100$), and Entity Match Score ($0-100$).
- **Multi-Location Ambiguity Detection**: Flags homonymous locations and provides actionable disambiguation guidance (e.g. `+ State name`, `+ PIN code`).
- **Directed Evidence Graph Model**: Graph nodes and directional relationships with explicit severity classifications (`INFO`, `WARNING`, `CONFLICT`) and Cytoscape/JSON export.
- **Interactive GIS Dashboard**: Dark-mode React + Leaflet interface with Address Interpretation card, Ambiguity card, Evidence Graph visualizer, Multi-Score gauges, and Leaflet layer toggles.

---

## 5. Measured Benchmark Results (1,065 Cases)

Empirical evaluation measured via the reproducible evaluation suite (`evaluation/run_benchmark.py`):

| Evaluation Metric | Phase 4 Baseline | Phase 5 Result | Improvement | Evaluation Objective |
| :--- | :---: | :---: | :---: | :--- |
| **Candidate Recall@5** | 44.40% | **98.74%** | **+54.34%** | Candidate pool coverage |
| **Candidate Recall@1** | 44.40% | **76.23%** | **+31.83%** | Top-ranked candidate accuracy |
| **Locality Accuracy** | 85.45% | **91.10%** | **+5.65%** | Locality/town/village resolution |
| **State Resolution Accuracy** | 88.61% | **88.61%** | Baseline | State entity identification |
| **District Resolution Accuracy** | 71.31% | **71.94%** | **+0.63%** | District entity resolution |
| **Exact Hierarchy Match** | 53.33% | **58.31%** | **+4.98%** | Simultaneous match across all 4 tiers |
| **Status Classification Accuracy** | 53.99% | **62.72%** | **+8.73%** | End-to-end verification accuracy |
| **PIN Code Accuracy** | 100.00% | **100.00%** | Maintained | Exact postal code validation |
| **Mean Pipeline Latency** | 3.69 ms | **35.11 ms** | Robust Multi-Stage | Full 9-channel candidate retrieval |

---

## 6. Verification Classifications

| Status | Meaning | Typical Scenario |
| :--- | :--- | :--- |
| `VERIFIED` | Strong geographic and administrative consistency. | Locality, subdistrict, district, state, coordinates, and PIN code fully align ($Score \ge 85$). |
| `CONSISTENT` | Most evidence agrees with minor omissions. | Valid address missing optional landmarks or sub-district ($Score \ge 70$). |
| `NEEDS_REVIEW` | Discrepancy or incomplete data requiring review. | PIN circle differs from state, or coordinate distance exceeds 20 km. |
| `INCONSISTENT` | Critical administrative/boundary mismatch. | `Kharadi, Kolhapur, Maharashtra` (Locality belongs to Pune, not Kolhapur). |
| `AMBIGUOUS` | Multiple geographic entities match. | `Rampur` without state, district, or PIN code disambiguation. |
| `UNABLE_TO_VERIFY`| Insufficient information. | Input cannot be parsed into recognizable geographic tokens. |

---

## 7. Technology Stack

### Backend & Evaluation
- **Python 3.11+ / 3.13**
- **FastAPI**: Asynchronous REST API framework
- **Pydantic v2**: Strict schemas and validation
- **SQLAlchemy 2.0**: ORM and relational models (PostGIS & SQLite support)
- **Shapely**: Point-in-polygon spatial containment
- **RapidFuzz**: High-performance fuzzy matching
- **Matplotlib**: Headless benchmark chart generation
- **Pytest**: **112 passing tests** (100% pass rate)

### Frontend
- **React 18 & Vite**
- **TypeScript**: Strict type safety
- **Tailwind CSS**: Professional dark GIS interface
- **Leaflet & React-Leaflet**: Interactive map rendering and GeoJSON layers
- **TanStack React Query**: Asynchronous state management
- **Lucide React**: Vector icons

---

## 8. Getting Started Locally

### 1. Clone the repository
```bash
git clone https://github.com/maneaditya478-commits/GeoVerify.git
cd GeoVerify
```

### 2. Set up Backend
```bash
# Create and activate virtual environment
python -m venv backend/.venv
.\backend\.venv\Scripts\Activate.ps1  # On Linux/macOS: source backend/.venv/bin/activate

# Install Python requirements
pip install -r backend/requirements.txt

# Run Data Ingestion & Transformation Pipeline
python data/scripts/download/fetch_sources.py
python data/scripts/transform/transform_admin_data.py
python data/scripts/generate_seed_data.py

# Start Backend Server
uvicorn app.main:app --app-dir backend --reload --port 8000
```
- Backend API: `http://localhost:8000`
- Swagger UI Docs: `http://localhost:8000/docs`

### 3. Set up Frontend
```bash
cd frontend
npm install
npm run dev
```
- Frontend: `http://localhost:5173`

---

## 9. Running Benchmarks & Tests

### Run Full Benchmark Suite (1,065 Cases)
```powershell
$env:PYTHONPATH="backend;. "
python -m evaluation.run_benchmark --dataset evaluation/datasets/benchmark.json --output-dir evaluation/results
```

### Run Candidate Recall Diagnostics Audit
```powershell
$env:PYTHONPATH="backend;. "
python -m evaluation.diagnose_recall
```

### Run Fast Smoke Benchmark (CI / Pre-commit)
```powershell
$env:PYTHONPATH="backend;. "
python -m evaluation.run_benchmark --smoke
```

### Run All Unit & Integration Tests (112 Tests)
```powershell
$env:PYTHONPATH="backend;. "
.\backend\.venv\Scripts\python -m pytest backend/tests evaluation/tests -v
```

### Frontend Typecheck & Build
```powershell
cd frontend
npm run build
```

---

## 10. Documentation Index

- [Multi-Stage Candidate Retrieval (Phase 5)](docs/candidate-retrieval-architecture.md)
- [Architecture Overview](docs/architecture.md)
- [Benchmark Methodology](docs/benchmark-methodology.md)
- [Evaluation Metrics & Formulas](docs/evaluation-metrics.md)
- [Diagnostic Error Analysis](docs/error-analysis.md)
- [Benchmark Dataset & Provenance](docs/benchmark-dataset.md)
- [Verification Methodology](docs/verification-methodology.md)
- [Address Entity Resolution](docs/address-resolution.md)
- [Multilingual & Transliteration](docs/multilingual-addresses.md)
- [Directed Evidence Model](docs/evidence-model.md)
- [Data Ingestion Pipeline](docs/data-pipeline.md)
- [Data Sources & Licensing](docs/data-sources.md)
- [API Reference](docs/api.md)

---

## 11. Privacy & Ethical Guidelines

1. **No Resident Profiling**: GeoVerify verifies geographic consistency, never personal residence.
2. **Data Minimization**: Submissions are not retained permanently by default.
3. **No Black-Box Arbitrary Classifications**: Every score is 100% transparent and deterministic.

---

## 12. License

This project is licensed under the [MIT License](LICENSE). Datasets are ingested under **GODL-India** and **ODbL**.
