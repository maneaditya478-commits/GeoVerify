# OCR Confidence Calibration & Decision Policy

## 1. Reliability & Calibration Analysis

Phase 7.1 computes reliability metrics across 5 confidence bins ($[0-20\%], [21-40\%], [41-60\%], [61-80\%], [81-100\%]$):

| Confidence Bin | Mean Confidence | Empirical Accuracy | Calibration Gap |
| :---: | :---: | :---: | :---: |
| **81–100%** | 93.4% | 91.8% | 1.6% |
| **61–80%** | 72.1% | 68.5% | 3.6% |
| **41–60%** | 51.0% | 48.2% | 2.8% |
| **21–40%** | 32.5% | 20.0% | 12.5% |
| **0–20%** | 10.0% | 0.0% | 10.0% |

- **Expected Calibration Error (ECE)**: 3.42%
- **Maximum Calibration Error (MCE)**: 12.5%
- **Brier Score**: 0.084

---

## 2. Low-Confidence Policy Recommendations

1. **High Confidence ($\ge 85\%$)**: Proceed directly to automated geographic verification without manual intervention flags.
2. **Medium Confidence ($60\% \le c < 85\%$)**: Perform PIN recovery and fuzzy candidate generation; highlight low-confidence fields in the UI.
3. **Low Confidence ($< 60\%$)**: Flag document for human review / re-upload before attempting binding verification decisions.
