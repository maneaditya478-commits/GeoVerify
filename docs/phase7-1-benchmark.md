# Phase 7.1 Benchmark Specification & Dataset

## 1. Benchmark Suite Breakdown

The Phase 7.1 Benchmark contains **105 standardized cases** partitioned into 60/20/20 splits:
- **Development Split (`DEV`)**: 63 cases (60%)
- **Validation Split (`VAL`)**: 21 cases (20%)
- **Frozen Held-Out Split (`HELD_OUT`)**: 21 cases (20%)

### Category Distribution:
1. `clean_documents` (15 cases): Standard utility and identity documents.
2. `multilingual_devanagari` (20 cases): Hindi and Marathi official records, revenue papers, and certificates.
3. `scan_degradations` (15 cases): Skewed (-7° to +12°), low contrast, low resolution, and blurry phone photos.
4. `ocr_noise_substitutions` (15 cases): Common character and digit OCR substitution corruptions.
5. `complex_multi_address` (15 cases): Invoices with billing vs shipping addresses, lease agreements, and corporate forms.
6. `multi_token_localities` (15 cases): Multi-word localities requiring compound entity matching.
7. `negative_adversarial` (10 cases): Non-address documents (PAN card front, payment receipts, code snippets, terms and conditions).

---

## 2. Running the Benchmark

Execute the complete diagnostic benchmark suite via:

```powershell
python evaluation/phase7_1/run_benchmark.py
```

Outputs will be generated in `evaluation/results/phase7_1/`.
