# Evaluation Metrics & Mathematical Formulation

## 1. Overview

GeoVerify India Phase 4 evaluates the address intelligence engine using a comprehensive suite of information retrieval, classification, and spatial verification metrics.

This document details the exact mathematical formulas, operational definitions, and interpretation guidelines for each metric computed by `evaluation/metrics.py`.

---

## 2. Multi-Tier Entity Resolution Metrics

Address resolution is evaluated at four administrative hierarchy levels plus strict multi-tier hierarchy alignment.

### 2.1 State Resolution Accuracy
Measures whether the resolved state entity matches the ground truth state.

$$\text{State Accuracy} = \frac{\sum_{i=1}^N \mathbb{I}(\hat{S}_i = S_i^*)}{N}$$

Where $\hat{S}_i$ is the predicted state, $S_i^*$ is the ground truth state, and $\mathbb{I}(\cdot)$ is the indicator function.

### 2.2 District Resolution Accuracy
Measures whether the resolved district entity matches the ground truth district.

$$\text{District Accuracy} = \frac{\sum_{i=1}^N \mathbb{I}(\hat{D}_i = D_i^*)}{N}$$

### 2.3 Sub-District / Taluka Resolution Accuracy
Evaluates matching at the sub-district level (Taluka in Maharashtra/Gujarat, Tehsil in UP/MP, Mandal in Telangana/AP). When ground truth does not specify a sub-district, cases with no predicted sub-district are considered correct.

$$\text{SubDistrict Accuracy} = \frac{\sum_{i=1}^N \mathbb{I}(\hat{T}_i = T_i^*)}{N}$$

### 2.4 Locality Resolution Accuracy
Measures whether the identified locality, town, or revenue village matches ground truth.

$$\text{Locality Accuracy} = \frac{\sum_{i=1}^N \mathbb{I}(\hat{L}_i = L_i^*)}{N}$$

### 2.5 Multi-Tier Exact Hierarchy Accuracy
Evaluates strict end-to-end alignment across all four administrative tiers simultaneously.

$$\text{Exact Hierarchy Accuracy} = \frac{\sum_{i=1}^N \mathbb{I}(\hat{S}_i = S_i^* \land \hat{D}_i = D_i^* \land \hat{T}_i = T_i^* \land \hat{L}_i = L_i^*)}{N}$$

### 2.6 PIN Code Resolution Accuracy
Measures matching of 6-digit postal code.

$$\text{PIN Code Accuracy} = \frac{\sum_{i=1}^N \mathbb{I}(\hat{P}_i = P_i^*)}{N}$$

---

## 3. Candidate Generation Retrieval Metrics ($\text{Recall@}K$)

For candidate generation and entity resolution, $\text{Recall@}K$ evaluates whether the true target entity appears within the top $K$ ranked candidates returned by the candidate generator.

Let $\mathcal{C}_i^{(K)} = \{c_{i,1}, c_{i,2}, \dots, c_{i,K}\}$ be the ordered list of top $K$ candidate entities for test record $i$, and let $e_i^*$ be the ground truth entity.

$$\text{Recall@}K = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(e_i^* \in \mathcal{C}_i^{(K)})$$

Standard operational evaluation evaluates:
- $\text{Recall@}1$: Top-ranked candidate accuracy
- $\text{Recall@}3$: Top-3 candidate inclusion
- $\text{Recall@}5$: Top-5 candidate inclusion
- $\text{Recall@}10$: Top-10 candidate retrieval ceiling

---

## 4. Ambiguity Detection Metrics

Ambiguity detection is framed as a binary classification task evaluating whether the system correctly detects homonymous locations requiring user disambiguation.

### 4.1 Contingency Matrix Definitions
- **True Positive ($TP$)**: Ambiguous address correctly flagged as `is_ambiguous = True`.
- **False Positive ($FP$)**: Unambiguous address incorrectly flagged as `is_ambiguous = True`.
- **True Negative ($TN$)**: Unambiguous address correctly left as `is_ambiguous = False`.
- **False Negative ($FN$)**: Ambiguous address missed and flagged as `is_ambiguous = False`.

### 4.2 Mathematical Formulas

$$\text{Precision}_{\text{ambig}} = \frac{TP}{TP + FP}$$

$$\text{Recall}_{\text{ambig}} = \frac{TP}{TP + FN}$$

$$\text{F1}_{\text{ambig}} = 2 \cdot \frac{\text{Precision}_{\text{ambig}} \cdot \text{Recall}_{\text{ambig}}}{\text{Precision}_{\text{ambig}} + \text{Recall}_{\text{ambig}}}$$

---

## 5. Verification Status Classification Metrics

The system classifies each input address into one of 6 mutually exclusive verification statuses:
$$\mathcal{S} = \{\text{VERIFIED}, \text{CONSISTENT}, \text{NEEDS\_REVIEW}, \text{INCONSISTENT}, \text{AMBIGUOUS}, \text{UNABLE\_TO\_VERIFY}\}$$

### 5.1 $6 \times 6$ Confusion Matrix
A matrix $M \in \mathbb{R}^{6 \times 6}$ where cell $M_{j, k}$ represents the count of test cases with expected status $j$ predicted as status $k$.

$$\text{Accuracy}_{\text{status}} = \frac{\sum_{j=1}^6 M_{j, j}}{\sum_{j=1}^6 \sum_{k=1}^6 M_{j, k}}$$

### 5.2 Per-Class and Macro/Weighted Averages
For each status class $c \in \mathcal{S}$:

$$\text{Precision}_c = \frac{M_{c, c}}{\sum_{j=1}^6 M_{j, c}}, \quad \text{Recall}_c = \frac{M_{c, c}}{\sum_{k=1}^6 M_{c, k}}, \quad F1_c = 2 \cdot \frac{\text{Precision}_c \cdot \text{Recall}_c}{\text{Precision}_c + \text{Recall}_c}$$

$$\text{Macro F1} = \frac{1}{|\mathcal{S}|} \sum_{c \in \mathcal{S}} F1_c$$

$$\text{Weighted F1} = \sum_{c \in \mathcal{S}} \left( \frac{N_c}{N} \cdot F1_c \right)$$

Where $N_c = \sum_{k=1}^6 M_{c, k}$ is the support for class $c$.

---

## 6. Score Distribution Statistics

For each continuous score generated by the engine ($\text{Consistency Score}$, $\text{Completeness Score}$, $\text{Entity Match Score}$), the evaluation computes summary statistics:

$$\mu = \frac{1}{N} \sum_{i=1}^N x_i, \quad \sigma = \sqrt{\frac{1}{N-1} \sum_{i=1}^N (x_i - \mu)^2}$$

$$\text{Median} = Q_{50}, \quad \text{Min} = \min(X), \quad \text{Max} = \max(X)$$

---

## 7. Latency Performance Percentiles

Micro-benchmarking measures execution time across $N$ iterations per component:

- **Mean Latency ($\bar{t}$)**: Arithmetic average latency.
- **Median / P50 ($t_{50}$)**: 50th percentile latency.
- **P90 ($t_{90}$)**: 90th percentile latency.
- **P95 ($t_{95}$)**: 95th percentile latency (SLA boundary).
- **P99 ($t_{99}$)**: 99th percentile tail latency.
