# Multilingual & Indic Address Parsing

## 1. Overview

Indian addresses are frequently written in regional Indian scripts (such as Devanagari for Hindi and Marathi), mixed Latin-Indic scripts, or using formal administrative prefixes (e.g., *गाव:* for village, *तालुका:* for sub-district, *जिल्हा:* for district).

GeoVerify India contains a dedicated **Indic Transliteration & Semantic Parsing Engine** (`app/services/transliteration.py`) that processes multilingual and mixed-script inputs deterministically.

---

## 2. Script Detection

GeoVerify detects the primary script of the input address string:

* **Latin:** Standard English letters (`a-z`, `A-Z`).
* **Devanagari:** Hindi / Marathi Unicode range (`\u0900-\u097F`).
* **Mixed:** Contains both Latin and Devanagari characters (e.g., `Kharadi, पुणे, Maharashtra 411014`).
* **Unknown:** Special symbols or unsupported scripts.

---

## 3. Indic Prefix Token Extraction

Addresses in rural and peri-urban India often follow formal government application structures with Indic administrative prefixes:

| Component | Indic Prefixes | English Prefixes |
| :--- | :--- | :--- |
| **Locality / Village** | `गाव:`, `गाँव:`, `ग्राम:`, `वस्ती:`, `मोहल्ला:`, `परिसर:` | `village:`, `locality:`, `area:` |
| **Sub-District / Taluka** | `तालुका:`, `तहसील:`, `तहसिल:`, `मंडळ:` | `taluka:`, `tehsil:`, `mandal:` |
| **District** | `जिल्हा:`, `जिला:`, `शहर:` | `district:`, `dist:`, `city:` |
| **State** | `राज्य:`, `प्रदेश:` | `state:`, `st:` |
| **PIN Code** | `पिन:`, `पिनकोड:`, `पिन कोड:` | `pin:`, `pincode:` |
| **Landmark** | `जवळ:`, `शेजारी:`, `जवळपास:`, `समोर:`, `मागे:` | `near:`, `opp:`, `behind:` |

### Example Transformation:
**Input:**
```
गाव: खराडी, तालुका: हवेली, जिल्हा: पुणे, राज्य: महाराष्ट्र, पिन: 411014
```
**Parsed Output:**
* Locality: `Kharadi`
* Sub-District: `Haveli`
* District: `Pune`
* State: `Maharashtra`
* PIN: `411014`
* Script: `Devanagari`
* Parse Confidence: `100%`

---

## 4. Devanagari-to-Latin Transliteration

The transliteration service matches against a curated, multi-tier gazetteer of Indian administrative entities:
* All 36 States & Union Territories (e.g., `महाराष्ट्र` $\rightarrow$ `Maharashtra`, `कर्नाटक` $\rightarrow$ `Karnataka`, `उत्तर प्रदेश` $\rightarrow$ `Uttar Pradesh`).
* Major Districts & Metros (e.g., `नवी दिल्ली` / `नई दिल्ली` $\rightarrow$ `New Delhi`, `पुणे` $\rightarrow$ `Pune`, `मुंबई` $\rightarrow$ `Mumbai Suburban`, `बंगळुरू` $\rightarrow$ `Bengaluru Urban`).
* Talukas & Sub-Districts (e.g., `हवेली` $\rightarrow$ `Haveli`, `मुळशी` $\rightarrow$ `Mulshi`, `शिरूर` $\rightarrow$ `Shirur`, `अंधेरी` $\rightarrow$ `Andheri`).
* Localities (e.g., `खराडी` $\rightarrow$ `Kharadi`, `हिंजवडी` $\rightarrow$ `Hinjewadi`, `कोथरूड` $\rightarrow$ `Kothrud`, `बाणेर` $\rightarrow$ `Baner`, `कनॉट प्लेस` $\rightarrow$ `Connaught Place`).

---

## 5. Mixed-Script Handling

When users enter hybrid addresses such as:
```
Flat 302, Kharadi, पुणे, Maharashtra 411014
```
The tokenizer extracts English and Devanagari tokens simultaneously, resolves `पुणे` to `Pune`, and validates the entire administrative chain seamlessly against the PostGIS/LGD database.
