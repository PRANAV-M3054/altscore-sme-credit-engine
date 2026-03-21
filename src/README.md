# ⚙️ Source Code — AltScore SME Credit Engine

> This directory contains all Python scripts powering the AltScore pipeline.
> Each script is self-contained, documented, and can be run independently.

---

## 📁 Folder Structure

```
src/
├── data/
│   ├── clean_data.py          ← Phase 2: Raw data cleaning pipeline
│   └── simulate_gst_data.py   ← Phase 2: GST data simulation (coming next)
│
├── feature_engineering/
│   └── build_features.py      ← Phase 4: Advanced feature engineering
│
├── models/
│   ├── train_model.py         ← Phase 5: XGBoost training
│   └── explain_model.py       ← Phase 5: SHAP explainability
│
├── llm/
│   ├── rejection_letter.py    ← Phase 6: Claude API rejection letters
│   ├── shap_narrative.py      ← Phase 6: Plain-English SHAP explanations
│   └── sql_chatbot.py         ← Phase 6: Text-to-SQL loan officer chatbot
│
└── api/
    └── main.py                ← Phase 7: FastAPI endpoints
```

---

## 🧹 clean_data.py

**Location:** `src/data/clean_data.py`
**Phase:** 2 — Data Cleaning
**Input:** `data/raw/application_data.csv` (307,511 rows, 122 columns)
**Output:** `data/processed/application_cleaned.csv` (307,511 rows, 111 columns)

### What it does

```
Raw CSV (122 cols)
      ↓
drop_high_missing()      →  drops 17 columns with >60% missing
      ↓
fix_days_columns()       →  converts negative days to AGE_YEARS, YEARS_EMPLOYED
      ↓
impute_missing()         →  fills remaining NaNs (median for numeric, mode for text)
      ↓
cap_outliers()           →  caps extreme values at 99th percentile
      ↓
engineer_base_features() →  creates 6 new features
      ↓
Clean CSV (111 cols)
```

### Functions breakdown

| Function | Input | Output | What it does |
|----------|-------|--------|-------------|
| `load_data(filepath)` | CSV path | DataFrame | Loads raw CSV, prints shape + default rate |
| `drop_high_missing(df, threshold)` | DataFrame | DataFrame | Drops columns with >60% missing values |
| `fix_days_columns(df)` | DataFrame | DataFrame | Converts DAYS_BIRTH → AGE_YEARS, fixes unemployed placeholder |
| `impute_missing(df)` | DataFrame | DataFrame | Fills NaN — median for numbers, mode for text |
| `cap_outliers(df)` | DataFrame | DataFrame | Clips extreme values at 99th percentile |
| `engineer_base_features(df)` | DataFrame | DataFrame | Creates 6 new engineered columns |
| `save_output(df, filepath)` | DataFrame + path | CSV file | Saves cleaned data to processed folder |

### Engineered features created

| Feature | Formula | Why it matters |
|---------|---------|----------------|
| `CREDIT_TO_INCOME_RATIO` | AMT_CREDIT / AMT_INCOME_TOTAL | Core risk signal — how much debt vs income |
| `ANNUITY_TO_INCOME_RATIO` | AMT_ANNUITY / (AMT_INCOME_TOTAL / 12) | Monthly repayment burden |
| `IS_SME` | 1 if Self-employed / Businessman / Commercial associate | Our SME identification flag |
| `INCOME_CATEGORY` | Bucketed income bands | Low / Medium / High / Very High |
| `HIGH_RISK_FLAG` | 1 if CREDIT_TO_INCOME_RATIO > 8 | Extreme leverage flag |
| `IS_STABLE_EMPLOYMENT` | 1 if YEARS_EMPLOYED >= 2 | Employment stability signal |

### Key findings after cleaning

```
Columns dropped (>60% missing)  :  17
Missing values remaining         :  0
SME applicants flagged           :  71,627  (23.3%)
High risk applicants             :  23,855  (7.7%)
Stably employed                  :  249,351 (81.1%)
AMT_INCOME_TOTAL max before cap  :  117,000,000
AMT_INCOME_TOTAL max after cap   :  472,500
Output file size                 :  181.4 MB
```

### How to run

```bash
# From project root
python src/data/clean_data.py
```

Expected output:
```
==================================================
AltScore — Data Cleaning Pipeline
==================================================
Shape: (307511, 122)
Default rate: 8.07 %
Columns to drop: 17
Shape after dropping: (307511, 105)
Unemployed placeholder replaced with NaN
AGE_YEARS min: 20.5 max: 69.1
YEARS_EMPLOYED missing: 55374
Missing values remaining: 0
AMT_INCOME_TOTAL — before max: 117,000,000 → after max: 472,500
...
Saved to: data/processed/application_cleaned.csv
File size: 181.4 MB
==================================================
Pipeline complete!
==================================================
```

### Design decisions

**Why drop columns with >60% missing instead of imputing them?**
Columns like `COMMONAREA_AVG` and `LANDAREA_MODE` are property-related details that are irrelevant for SME credit scoring. Imputing 70% of a column's values introduces more noise than signal — dropping is the cleaner choice.

**Why median imputation and not mean?**
Financial data has extreme outliers (e.g., income of 117M). The mean gets pulled toward these extremes. The median — the middle value — is unaffected by outliers and gives a more representative fill value.

**Why cap at 99th percentile and not drop outlier rows?**
Dropping outlier rows loses real applicants from our training data. Capping clips the value to a reasonable ceiling while keeping the row — the applicant still exists, their income is just bounded.

---

## 🔜 Coming Next

| Script | Phase | Status |
|--------|-------|--------|
| `simulate_gst_data.py` | Phase 2 | Next up |
| `build_features.py` | Phase 4 | Upcoming |
| `train_model.py` | Phase 5 | Upcoming |
| `explain_model.py` | Phase 5 | Upcoming |
| `rejection_letter.py` | Phase 6 | Upcoming |
| `sql_chatbot.py` | Phase 6 | Upcoming |
| `main.py` (FastAPI) | Phase 7 | Upcoming |

---

*Last updated: March 2026*
*Project: AltScore — SME Credit Intelligence Engine*
