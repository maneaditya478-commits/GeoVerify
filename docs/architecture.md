# GeoVerify India Architecture (Phase 4)

## 1. System Overview

GeoVerify India is an open-source, multi-signal geospatial and administrative consistency verification platform designed specifically for the complexities of Indian addresses.

```mermaid
flowchart TD
    User([User / API Client]) -->|Submit Address| API[FastAPI Gateway]
    
    subgraph IndicLayer [Multilingual & Transliteration Layer]
        API --> Script["Script Detector (Latin / Devanagari / Mixed)"]
        Script --> Prefix["Indic Prefix Extractor (गाव/तालुका/जिल्हा)"]
        Prefix --> Translit["Devanagari-to-Latin Transliteration"]
    end

    subgraph EntityResolution [Address Entity Resolution Layer]
        Translit --> CandGen["Candidate Entity Generator (LGD + Postal Gazetteers)"]
        CandGen --> Matcher["Multi-Factor Entity Matcher (0-100)"]
        Matcher --> Ambiguity["Ambiguity Detector (Score Delta & Jurisdiction)"]
        Matcher --> Completeness["Address Completeness Evaluator (0-100)"]
    end

    subgraph VerificationPipeline [GIS & Multi-Signal Pipeline]
        EntityResolution --> Norm[1. Address Normalizer]
        Norm --> Parse[2. Structured Parser (Premise, Taluka, PIN)]
        Parse --> Geo[3. Geocoding Provider Layer]
        
        Geo --> Hier["4. Multi-Tier Hierarchy (Country ➔ State ➔ District ➔ Taluka ➔ Locality)"]
        Geo --> Bound["5. Point-in-Polygon Boundaries (State, District, Taluka)"]
        Geo --> Pin["6. PIN Code Validator (Format, Circle, Centroid Distance)"]
        Geo --> Near["7. Nearby Context (Transit, Hospitals, POIs)"]
        
        Hier --> Evid[8. Evidence & Explainability Engine]
        Bound --> Evid
        Pin --> Evid
        Near --> Evid
    end
    
    subgraph EvidenceGraphLayer [Directed Evidence Graph Layer]
        Evid --> GraphBuilder["Evidence Graph Builder (Nodes & Directed Edges)"]
        GraphBuilder --> Severity["Edge Severity Evaluator (INFO / WARNING / CONFLICT)"]
        Severity --> GraphSerializer["Graph Serializer (JSON / Cytoscape)"]
    end

    subgraph ScoringLayer [Multi-Score Evaluation Engine]
        Evid --> Score1["Geographic Consistency Score (0-100)"]
        Completeness --> Score2["Address Completeness Score (0-100)"]
        Matcher --> Score3["Entity Match Score (0-100)"]
    end

    subgraph EvaluationFramework [Phase 4 Evaluation & Benchmarking Subsystem]
        Dataset["Benchmark Dataset (1,065 Cases)"] --> BenchRunner["Benchmark Runner CLI"]
        BenchRunner --> PipelinePerf["Latency Micro-Benchmarker"]
        BenchRunner --> MetricsEngine["Multi-Tier Metrics Engine"]
        BenchRunner --> DiagnosticAnalyzer["12-Bucket Error Analyzer"]
        MetricsEngine --> Visualizer["Matplotlib Chart Visualizer (7 Figures)"]
        MetricsEngine --> ReportGen["Markdown Report Generator"]
    end

    ScoringLayer --> Result[Verification Response + Evidence Graph + GeoJSON + Data Sources]
    Result --> Frontend[React / Vite / Leaflet GIS UI]
```

---

## 2. Core Subsystems

### 2.1 Multilingual & Transliteration Layer (`app/services/transliteration.py`)
- Detects input script: `Latin`, `Devanagari`, or `Mixed`.
- Extracts Indic administrative prefix tokens:
  - Locality: `गाव:`, `गाँव:`, `ग्राम:`, `वस्ती:`
  - Taluka: `तालुका:`, `तहसील:`, `मंडळ:`
  - District: `जिल्हा:`, `जिला:`, `शहर:`
  - State: `राज्य:`, `प्रदेश:`
  - PIN: `पिन:`, `पिनकोड:`
- Transliterates Devanagari entities into canonical English equivalents using official gazetteer mappings.

### 2.2 Address Entity Resolution Layer (`app/entity_resolution/`)
- `CandidateGenerator`: Queries indexed LGD and postal catalogs via exact, alias, transliteration, and fuzzy matching.
- `EntityMatcher`: Computes a transparent 5-factor Entity Match Score ($0 - 100$): Name similarity ($40\%$), Administrative context ($25\%$), PIN compatibility ($15\%$), Geographic proximity ($15\%$), Entity level weight ($5\%$).
- `AmbiguityDetector`: Flags multi-location ambiguities when candidate score delta $\le 12.0$ across different administrative jurisdictions.
- `AddressEntityResolver`: Orchestrates candidate generation, match scoring, ambiguity detection, and completeness evaluation.

### 2.3 Directed Evidence Graph Layer (`app/evidence/`)
- `EvidenceGraphBuilder`: Assembles nodes (Country, State, District, Sub-District, Locality, PIN, Coordinates, POIs) and directional relationships (`located_in`, `inside_polygon`, `postal_area_of`, `in_vicinity_of`, `mismatch_with`).
- `EdgeSeverity`: Classifies relationships as `INFO` (consistent), `WARNING` (minor distance or missing parent), or `CONFLICT` (administrative boundary contradiction).
- `EvidenceGraphSerializer`: Serializes graph to JSON and Cytoscape formats.

### 2.4 Administrative Hierarchy Engine (`app/verification/hierarchy.py`)
- Enforces multi-tier Indian administrative structure:
  $$\text{Country} \rightarrow \text{State} \rightarrow \text{District} \rightarrow \text{Sub-District (Taluka/Tehsil)} \rightarrow \text{Locality}$$
- Validates cross-level containment and detects mismatches.

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

### 2.7 Multi-Score Evaluation System (`app/verification/scoring.py`)
Produces 3 transparent, deterministic scores:
1. **Geographic Consistency Score** ($0 - 100$): Cross-signal administrative, geometric, and postal alignment.
2. **Address Completeness Score** ($0 - 100$): Presence of premise, locality, district, state, and PIN.
3. **Entity Match Score** ($0 - 100$): Gazetteer resolution confidence for identified entities.

### 2.8 Benchmarking & Evaluation Subsystem (`evaluation/`)
- `BenchmarkRunner`: End-to-end CLI with smoke tests, custom sizes, and seeds.
- `MetricsEngine`: Computes multi-tier accuracies, $\text{Recall@}K$, ambiguity precision/recall/F1, and $6 \times 6$ confusion matrices.
- `DiagnosticErrorAnalyzer`: Maps failures into 12 structured diagnostic failure buckets.
- `PerformanceProfiler`: Measures per-component micro-latencies across percentiles (P50, P90, P95, P99).
- `VisualizationEngine`: Generates 7 headless publication-grade Matplotlib plots.
- `ReportGenerator`: Produces Markdown reports summarizing empirical findings.
