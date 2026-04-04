# 🗄️ Database — AltScore SME Credit Engine

> PostgreSQL 18 star schema storing all loan application,
> GST simulation, and ML prediction data.

---

## 📐 Star Schema Design

```
                    dim_business
                    (who applied?)
                         |
                         |
dim_cashflow ——— fact_loan_applications ——— dim_gst
(financials)      (one row per applicant)   (GST signals)
                         |
                         |
                    ml_predictions
                    (model outputs)
```

**Why star schema?**
Star schema is the standard for analytical databases (data warehouses).
The fact table holds measurable events (loan applications), dimension
tables hold descriptive context (who, what, how much). This structure
makes Power BI queries fast and intuitive.

---

## 📋 Table Reference

### fact_loan_applications (central table)

| Column | Type | Description |
|--------|------|-------------|
| SK_ID_CURR | INTEGER PK | Unique applicant ID |
| TARGET | INTEGER | 1 = defaulted, 0 = repaid |
| AGE_YEARS | FLOAT | Applicant age in years |
| YEARS_EMPLOYED | FLOAT | Years at current employer |
| REGION_RATING_CLIENT | INTEGER | Bank's regional risk rating |
| EXT_SOURCE_1 | FLOAT | External credit score 1 |
| EXT_SOURCE_2 | FLOAT | External credit score 2 |
| EXT_SOURCE_3 | FLOAT | External credit score 3 |
| ML_RISK_SCORE | FLOAT | XGBoost prediction (added Phase 5) |
| ML_RISK_TIER | VARCHAR | Low / Medium / High risk tier |
| CREATED_AT | TIMESTAMP | Record creation time |

### dim_business

| Column | Type | Description |
|--------|------|-------------|
| SK_ID_CURR | INTEGER PK | Links to fact table |
| NAME_INCOME_TYPE | VARCHAR | Employment type |
| NAME_EDUCATION_TYPE | VARCHAR | Education level |
| ORGANIZATION_TYPE | VARCHAR | Employer organisation type |
| IS_SME | INTEGER | 1 = SME applicant, 0 = other |
| INCOME_CATEGORY | VARCHAR | Low / Medium / High / Very High |

### dim_cashflow

| Column | Type | Description |
|--------|------|-------------|
| SK_ID_CURR | INTEGER PK | Links to fact table |
| AMT_INCOME_TOTAL | FLOAT | Annual income (capped at 99th pct) |
| AMT_CREDIT | FLOAT | Loan amount requested |
| AMT_ANNUITY | FLOAT | Monthly repayment amount |
| CREDIT_TO_INCOME_RATIO | FLOAT | Credit / Income — core risk signal |
| ANNUITY_TO_INCOME_RATIO | FLOAT | Monthly burden as % of income |
| HIGH_RISK_FLAG | INTEGER | 1 if credit ratio > 8 |
| IS_STABLE_EMPLOYMENT | INTEGER | 1 if employed >= 2 years |

### dim_gst (alternative credit signals)

| Column | Type | Description |
|--------|------|-------------|
| SK_ID_CURR | INTEGER PK | Links to fact table |
| GST_REGISTERED | INTEGER | 1 = GST registered business |
| GST_FILING_COMPLIANCE | FLOAT | % of quarters filed on time (0-1) |
| GST_QUARTERLY_TURNOVER | FLOAT | Average quarterly revenue |
| GST_TURNOVER_GROWTH | FLOAT | Revenue growth trend (-1 to 1) |
| GST_FILING_STREAK | INTEGER | Consecutive on-time quarters (0-8) |
| CASH_FLOW_RATIO | FLOAT | Monthly inflow vs outflow ratio |
| GST_PENALTY_COUNT | INTEGER | Late filing penalties (0-5) |

### ml_predictions (populated in Phase 5)

| Column | Type | Description |
|--------|------|-------------|
| PREDICTION_ID | SERIAL PK | Auto-increment ID |
| SK_ID_CURR | INTEGER | Links to applicant |
| ML_RISK_SCORE | FLOAT | XGBoost probability score |
| ML_RISK_TIER | VARCHAR | Low / Medium / High |
| SHAP_TOP_FEATURE_1/2/3 | VARCHAR | Top 3 risk factors from SHAP |
| LLM_REJECTION_LETTER | TEXT | Claude API generated letter |
| PREDICTED_AT | TIMESTAMP | When prediction was made |

---

## ⚙️ Setup Instructions

### Step 1 — Install PostgreSQL 18
Download from https://www.postgresql.org/download/windows/

### Step 2 — Create database
```bash
psql -U postgres
CREATE DATABASE altscore_db;
\q
```

### Step 3 — Run schema file
```bash
psql -U postgres -d altscore_db -f database/schema.sql
```

### Step 4 — Load data
```bash
python src/data/load_to_db.py
```

### Step 5 — Verify
```bash
psql -U postgres -d altscore_db
SELECT COUNT(*) FROM fact_loan_applications;
-- Should return 307511
```

---

## 🔍 Key Queries

### Default rate by income type
```sql
SELECT "NAME_INCOME_TYPE",
       COUNT(*) AS total,
       ROUND(AVG(f."TARGET")::numeric * 100, 2) AS default_rate
FROM fact_loan_applications f
JOIN dim_business b ON f."SK_ID_CURR" = b."SK_ID_CURR"
GROUP BY "NAME_INCOME_TYPE"
ORDER BY default_rate DESC;
```

### GST compliance vs default rate
```sql
SELECT f."TARGET",
       ROUND(AVG(g."GST_FILING_COMPLIANCE")::numeric, 3) AS avg_compliance,
       ROUND(AVG(g."CASH_FLOW_RATIO")::numeric, 3) AS avg_cashflow
FROM fact_loan_applications f
JOIN dim_gst g ON f."SK_ID_CURR" = g."SK_ID_CURR"
GROUP BY f."TARGET"
ORDER BY f."TARGET";
```

### High risk SME applicants
```sql
SELECT COUNT(*) AS high_risk_sme
FROM fact_loan_applications f
JOIN dim_business b ON f."SK_ID_CURR" = b."SK_ID_CURR"
JOIN dim_cashflow c ON f."SK_ID_CURR" = c."SK_ID_CURR"
WHERE b."IS_SME" = 1
AND c."HIGH_RISK_FLAG" = 1;
```

---

## 📊 Database Stats

```
Total applicants     :  307,511
SME applicants       :   71,627  (23.3%)
Default rate         :    8.07%
High risk applicants :   23,855  (7.7%)
Tables               :        4
Views                :        2
Database size        :    ~180MB
```

---

*Database: altscore_db*
*Engine: PostgreSQL 18*
*Project: AltScore — SME Credit Intelligence Engine*
