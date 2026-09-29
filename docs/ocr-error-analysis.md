# OCR Error Analysis & Character Degradation

## 1. Overview

Optical Character Recognition (OCR) applied to real-world Indian documents (utility bills, receipts, identity cards, trade licenses) encounters unique visual noise and glyph confusions.

---

## 2. Common Character & Digit Confusions in Indian Addresses

| OCR Character Confusion | Example Raw Token | Clean Ground Truth | Correction Strategy |
| :--- | :--- | :--- | :--- |
| **O / o / D / Q $\to$ 0** | `411O14`, `56OO38` | `411014`, `560038` | Positional digit substitution in 6-character PIN tokens |
| **I / l / \| / ! $\to$ 1** | `I10001`, `41l014` | `110001`, `411014` | Alphanumeric repair requiring $\ge 3$ native digits |
| **S / $ $\to$ 5** | `S60066`, `4110$7` | `560066`, `411057` | Leading digit substitution ($1\dots 9$) |
| **B / & $\to$ 8** | `40005B` | `400058` | Trailing digit repair |
| **Z / z $\to$ 2** | `30Z021` | `302021` | Postal PIN token substitution table |
| **०, १, २, ३, ४, ५, ६, ७, ८, ९ $\to$ 0..9** | `४११०१४` | `411014` | Devanagari unicode translation mapping |

---

## 3. Administrative Keyword OCR Fixes

OCR engines frequently garble standard administrative keywords in scanned headers:

```text
"Ta1uka:"   → "Taluka"
"D1st:"     → "District"
"P1n code"  → "Pincode"
"M@h@r@shtr@" → "Maharashtra"
"K@rn@t@k@" → "Karnataka"
"Tehs11"    → "Tehsil"
```

These are repaired by regex replacement patterns prior to address region parsing.

---

## 4. Degradation Impact Analysis

Comparing clean typed address strings against OCR-extracted text from image renderings:

- **Recall@1 Retention**: 88.5%
- **Recall@5 Retention**: 99.1%
- **District Accuracy Retention**: 92.6%
- **Locality Accuracy Retention**: 80.9%

The biggest degradation factor occurs in low-contrast thermal receipts and extreme skew (>10°), which are mitigated by PIL-based adaptive contrast enhancement and deskew rotation.
