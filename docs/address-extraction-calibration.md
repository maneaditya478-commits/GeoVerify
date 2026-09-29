# Address Extraction Calibration & Provenance Tracking

## 1. Field Extraction Provenance Model

Every extracted address field carries an explicit provenance tag indicating how it was obtained:

```python
class ExtractionMethod(str, Enum):
    EXPLICIT = "EXPLICIT"                       # Direct text token match in OCR output
    PIN_RECOVERY = "PIN_RECOVERY"               # Inferred from validated 6-digit PIN metadata
    ADMIN_CONTEXT_RECOVERY = "ADMIN_CONTEXT_RECOVERY" # Inferred from hierarchy parent/child relationships
    OCR_REPAIRED = "OCR_REPAIRED"               # Repaired from corrupted OCR alphanumeric glyphs
    INFERRED = "INFERRED"                       # Resolved during entity candidate generation
```

This ensures full explainability and prevents hallucinated inferences from masquerading as explicit document text.

---

## 2. Multi-Token Locality Calibration

### Challenge
In Indian addresses, localities often consist of 2 to 4 tokens (e.g. *Viman Nagar*, *Bandra West*, *Salt Lake Sector V*, *Connaught Place*, *DLF Cyber City*, *Koramangala 4th Block*). Naive tokenization splits these into separate premise/street fragments.

### Solution
1. **Direct Dictionary Matching**: `KNOWN_LOCALITIES` and `KNOWN_SUBDISTRICTS` are evaluated with length-descending greedy phrase matching.
2. **Post-Position Binding**: Compound words following road/phase markers (*Phase 1*, *Sector 25*, *Block EP*) are grouped into cohesive locality entities.

---

## 3. UI Representation

In the GeoVerify web interface (`frontend/src/components/ExtractedFieldsTable.tsx`), extraction methods are displayed as color-coded badges:
- **`EXPLICIT`**: Standard direct extract
- **`PIN RECOVERY`**: Amber badge with PIN postal mapping explanation
- **`OCR REPAIRED`**: Blue badge detailing the character substitution fix
- **`ADMIN CONTEXT RECOVERY`**: Purple badge highlighting hierarchy inheritance
