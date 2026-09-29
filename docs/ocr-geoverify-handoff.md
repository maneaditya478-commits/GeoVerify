# OCR-to-GeoVerify Handoff Architecture & Protocol

## 1. Architectural Philosophy & Invariants

The handoff boundary between the Document Processing / OCR subsystem and the Core Geographic Verification Engine is governed by strict system invariants:

> **Invariant 1:** OCR extracts evidence. GeoVerify verifies geographic consistency.
> 
> **Invariant 2:** OCR confidence is NOT geographic validity. A high OCR token confidence score (e.g. 0.99) on an imaginary or non-existent PIN/locality must never result in a `VERIFIED` status.
> 
> **Invariant 3:** Missing evidence is NOT conflicting evidence. An OCR-extracted address lacking premise or street numbers represents a partial address, not a geographic contradiction.

```
+------------------------------------------------------------------------------------+
|                             DOCUMENT OCR SUBSYSTEM                                 |
|  [Document / Image / PDF]                                                          |
|         │                                                                          |
|         ▼                                                                          |
|  [Image Preprocessing & OCR Engine] ──► Extracted Bounding Boxes & Raw Tokens      |
|         │                                                                          |
|         ▼                                                                          |
|  [Address Region Detector] ───────────► Address Bounding Bboxes                    |
|         │                                                                          |
|         ▼                                                                          |
|  [Field Extractor & OCR Normalizer] ──► ExtractedAddressField (with Provenance)    |
|         │                                                                          |
|         ▼                                                                          |
|  [PIN-First Recovery Service] ────────► ExtractedAddressCandidate                  |
+──────────────────────────────────────────────────┬─────────────────────────────────+
                                                   │ Handoff Boundary
                                                   ▼
+──────────────────────────────────────────────────┴─────────────────────────────────+
|                        GEOVERIFY VERIFICATION SUBSYSTEM                            |
|  [Candidate Generator & Fuzzy Retrieval]                                           |
|         │                                                                          |
|         ▼                                                                          |
|  [Context-Aware Ranking & Ambiguity Calibration]                                   |
|         │                                                                          |
|         ▼                                                                          |
|  [Geographic Verification & Evidence Graph Analysis]                              |
|         │                                                                          |
|         ▼                                                                          |
|  [Calibrated Decision Engine] ────────► VerificationResponse (VERIFIED / CONSISTENT)|
+------------------------------------------------------------------------------------+
```

---

## 2. Structured Handoff Schema

The handoff protocol transfers an `ExtractedAddressCandidate` from the Document subsystem to the GeoVerify engine:

```python
class ExtractedAddressCandidate(BaseModel):
    candidate_id: str
    address_type: DocumentAddressType = DocumentAddressType.RESIDENTIAL
    raw_address_text: str
    assembled_address: str
    structured_components: Dict[str, str] = Field(default_factory=dict)
    fields: Dict[str, ExtractedAddressField] = Field(default_factory=dict)
    confidence: float
    page_num: int = 1
    region_bbox: Optional[BoundingBox] = None
    provenance: Dict[str, Any] = Field(default_factory=dict)
    pin_recovered: bool = False
```

Each field carries explicit extraction provenance:
- `EXPLICIT`: Directly recognized from document text.
- `PIN_RECOVERY`: Inferred from postal database via a verified 6-digit PIN code.
- `ADMIN_CONTEXT_RECOVERY`: Inferred from unambiguous parent administrative hierarchy.
- `OCR_REPAIRED`: Recovered through OCR character confusion heuristics (e.g. S60066 → 560066).

---

## 3. Evidence Propagation into GeoVerify

When `DocumentProcessingPipeline` processes a candidate into the verification engine, the fields are converted into a `VerificationRequest`:

```python
verification_request = VerificationRequest(
    address=candidate.assembled_address,
    pincode=candidate.fields.get("pincode", {}).normalized_value,
    locality=candidate.fields.get("locality", {}).normalized_value,
    subdistrict=candidate.fields.get("subdistrict", {}).normalized_value,
    district=candidate.fields.get("district", {}).normalized_value,
    state=candidate.fields.get("state", {}).normalized_value,
)
```

### Provenance Weighting in Evidence Scoring:
- `EXPLICIT` fields contribute 100% evidence strength ($W = 1.0$).
- `OCR_REPAIRED` fields contribute 95% evidence strength ($W = 0.95$).
- `PIN_RECOVERY` administrative fields contribute 85% evidence strength ($W = 0.85$).
- `ADMIN_CONTEXT_RECOVERY` fields contribute 80% evidence strength ($W = 0.80$).

This ensures that administrative fields filled by PIN inference confirm geographic consistency without artificially boosting premise-level completeness.
