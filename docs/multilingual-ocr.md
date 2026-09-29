# Multilingual OCR & Indic Robustness

## 1. Multilingual Scope

GeoVerify Phase 7.1 supports multi-script documents containing:
- **Latin Script**: Standard English text.
- **Devanagari Script**: Hindi and Marathi official records, land 7/12 extracts, municipal receipts, domicile certificates.
- **Mixed Bilingual**: Documents featuring side-by-side or interleaved English and Indic labels.

---

## 2. Key Indic Parsing Features

### 1. Devanagari Numeral Conversion
Devanagari numerals (`०१२३४५६७८९`) in PIN codes, house numbers, and wards are normalized to standard Arabic numerals (`0123456789`) prior to regex extraction.

### 2. Abbreviated Administrative Prefixes
Official revenue and municipal documents frequently use period-delimited abbreviations:
- `जि.` / `जिल्हा:` $\to$ District
- `ता.` / `तालुका:` $\to$ Sub-district / Taluka
- `गा.` / `गाव:` $\to$ Village / Locality

Updated regex patterns accommodate periods, colons, hyphens, and whitespace variations.

### 3. Transliteration & Phonetic Expansion
The transliteration service (`app.services.transliteration`) maps Devanagari place names (e.g., `वाराणसी`, `इंदौर`, `पटना`, `रायपुर`, `पुणे`, `कोथरूड`, `हडपसर`) into canonical English administrative entities for candidate matching.
