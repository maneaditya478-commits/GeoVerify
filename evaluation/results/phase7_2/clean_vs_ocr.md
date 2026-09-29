# Clean Text vs OCR Address Verification Control Experiment (Phase 7.2)

## 1. Summary Comparison

| Metric | Clean Ground-Truth Input | OCR-Derived Input | Delta | Retention |
| :--- | :---: | :---: | :---: | :---: |
| **Locality Match Rate** | 50.83% | 46.67% | -4.17% | 91.8% |
| **District Match Rate** | 69.17% | 63.33% | -5.83% | 91.6% |
| **Status Accuracy** | 86.25% | 72.08% | -14.17% | 83.6% |

## 2. Paired Behavioral Classifications

- **Total Evaluated Address Pairs**: 240
- **OCR Did Not Change Ranking**: 151 (62.9%)
- **Same Resolution, Different Status (Decision Discrepancy)**: 16 (6.7%)
