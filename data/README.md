# 📂 Data Directory — AltScore SME Credit Engine

> This directory contains all data used in the AltScore pipeline.
> Raw files are **not committed to Git** (too large + sensitive).
> This README tells you exactly what data we use, where to get it, and what we found.

---

## 📁 Folder Structure

```
data/
├── raw/                  ← Original files, never modified
│   ├── application_data.csv
│   ├── previous_application.csv
│   └── columns_description.csv
│
├── processed/            ← Cleaned outputs from Python pipeline
│   ├── application_cleaned.csv
│   └── application_cleaned_sample.xlsx   ← Excel profiling (5000 rows)
│
└── simulated/            ← Synthetic GST data we generate
    └── gst_data.csv
```

---

## 📥 How to Get the Raw Data

### Step 1 — Create a Kaggle Account
Go to [kaggle.com](https://www.kaggle.com) and sign up (free).

### Step 2 — Download the Dataset

**Option A — Manual download:**
1. Visit 👉 https://www.kaggle.com/datasets/mishra5001/credit-card
2. Click the **Download** button
3. Unzip and place all CSV files inside `data/raw/`

**Option B — Kaggle API:**
```bash
pip install kaggle
kaggle datasets download -d mishra5001/credit-card -p data/raw --unzip
```

### Step 3 — Generate Simulated GST Data
```bash
python src/data/simulate_gst_data.py
```
This creates `data/simulated/gst_data.csv` with synthetic GST filing records for all applicants — our **key differentiator** from standard credit scoring projects.

---

## 🗂️ Dataset Overview

| File | Rows | Columns | Size | Description |
|------|------|---------|------|-------------|
| `application_data.csv` | 307,511 | 122 | 162 MB | Main loan application records |
| `previous_application.csv` | 1,670,214 | 37 | 395 MB | Historical loan behaviour per applicant |
| `columns_description.csv` | 122 | 3 | 28 KB | Data dictionary for all columns |
| `gst_data.csv` | 307,511 | 12 | ~45 MB | Simulated GST filing records (generated) |

---

## 🔍 Key Findings from Excel Profiling

> Profiling was done on a 5,000-row sample in Excel before automating the full pipeline in Python.
> See `data/processed/application_cleaned_sample.xlsx` → `Profiling` sheet for full documentation.

### Dataset Shape
```
Total applicants   :  307,511
Total features     :  122 columns
Target variable    :  TARGET (1 = defaulted, 0 = repaid)
```

### Class Distribution (Imbalance Alert)
```
Non-defaulters (0) :  282,686  →  91.93%
Defaulters     (1) :   24,825  →   8.07%
```
⚠️ Dataset is heavily imbalanced — handled using **SMOTE** in the ML pipeline.

### SME Applicant Breakdown
```
Self-employed        :  38,412
Commercial associate :  71,617
Businessman          :      10
─────────────────────────────
Total SME applicants : ~110,039  (35.8% of dataset)
```

### Credit-to-Income Ratio Analysis
```
Maximum  :  34.92  ← extreme risk (35x income borrowed)
Minimum  :   0.14  ← very conservative borrower
Average  :   3.95  ← dataset benchmark
Risk flag:  > 8.0  ← flagged as HIGH RISK in our model
```

### Missing Value Summary
```
Columns with >60% missing  :  23 columns  → DROPPED
Columns with 10–60% missing:  18 columns  → IMPUTED (median/mode)
Columns with <10% missing  :  26 columns  → IMPUTED (median/mode)
Columns with 0% missing    :  55 columns  → KEPT AS-IS
```

### Top Columns Dropped (>60% missing)
| Column | Missing % | Reason |
|--------|-----------|--------|
| COMMONAREA_AVG/MODE/MEDI | 69.87% | Property detail, irrelevant for SME |
| NONLIVINGAPARTMENTS_* | 69.43% | Property detail, irrelevant for SME |
| LIVINGAPARTMENTS_* | 68.35% | Property detail, irrelevant for SME |
| YEARS_BUILD_* | 66.50% | Property detail, irrelevant for SME |
| OWN_CAR_AGE | 65.99% | Not a credit risk signal |

---

## 🧹 Cleaning Rules Documented in Excel → Automated in Python

| # | Issue Found | Action Taken |
|---|------------|-------------|
| 1 | `DAYS_BIRTH` stored as negative days | Converted to `AGE_YEARS` (positive) |
| 2 | `DAYS_EMPLOYED = 365243` placeholder | Replaced with `NaN` (means unemployed) |
| 3 | `DAYS_EMPLOYED` stored as negative | Converted to `YEARS_EMPLOYED` (positive) |
| 4 | 23 columns with >60% missing | Dropped entirely |
| 5 | `EXT_SOURCE_1` — 56% missing | Imputed with median |
| 6 | `AMT_ANNUITY` — 12 missing rows | Imputed with median |
| 7 | `AMT_GOODS_PRICE` — 278 missing | Imputed with median |
| 8 | Extreme income outlier (`117,000,000`) | Capped at 99th percentile |

---

## ⚙️ Engineered Features (Created in Python)

These features were **designed by us** — not present in the original dataset:

| Feature | Formula | Why It Matters |
|---------|---------|----------------|
| `CREDIT_TO_INCOME_RATIO` | AMT_CREDIT / AMT_INCOME_TOTAL | Core risk signal |
| `ANNUITY_TO_INCOME_RATIO` | AMT_ANNUITY / AMT_INCOME_TOTAL | Monthly repayment burden |
| `AGE_YEARS` | DAYS_BIRTH / -365 | Applicant age in years |
| `YEARS_EMPLOYED` | DAYS_EMPLOYED / -365 | Employment stability |
| `IS_SME` | IF income type = Self-employed etc. | Our SME flag |
| `INCOME_CATEGORY` | Bucketed income bands | Segment analysis |
| `GST_COMPLIANCE_SCORE` | From simulated GST data | Alternative credit signal |
| `CASH_FLOW_VELOCITY` | Monthly inflow / outflow ratio | Business health proxy |

---

## 📊 Running the Full Pipeline

```bash
# Step 1 — Clean raw data (outputs to data/processed/)
python src/data/clean_data.py

# Step 2 — Generate GST simulation
python src/data/simulate_gst_data.py

# Step 3 — Run feature engineering
python src/feature_engineering/build_features.py

# Step 4 — Open EDA notebook
jupyter notebook notebooks/01_eda.ipynb
```

---

*Data profiling completed: March 2026*  
*Project: AltScore — SME Credit Intelligence Engine*
