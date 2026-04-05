# 🏦 AltScore — SME Credit Intelligence Engine

> AI-powered alternative credit scoring for Indian small businesses using GST filing patterns, cash flow behaviour, and machine learning.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0-red)
![Groq](https://img.shields.io/badge/LLM-Groq%20Llama3-purple)

---

## 🎯 The Problem

India has **63 million SMEs**. Over **80% are rejected** by banks because they have no credit history — no home loan, no credit card, nothing in the CIBIL system. Banks call this a **"thin file"**.

But these businesses have real financial activity:
- GST filings every quarter
- UPI and bank transactions daily
- Cash flow patterns monthly

Traditional credit scoring **ignores all of this**.

---

## 💡 The Solution

AltScore builds an **alternative credit intelligence engine** that scores SMEs using behavioral and transactional signals instead of bureau scores.

```
Traditional Bank          AltScore
─────────────────         ──────────────────────────────
CIBIL score only    →     GST compliance patterns
Rejects thin files  →     Cash flow behaviour analysis
Manual decisions    →     XGBoost ML model (AUC 0.9999)
No explanation      →     SHAP explainability
Generic letters     →     AI-generated rejection letters
SQL knowledge needed→     Plain English chatbot
```

---

## 🚀 Live Demo — Streamlit Web App

The project ships with a full web application with 4 pages:

### 🏠 Home Page
Project overview with live KPI metrics from the database.

### 📋 Loan Eligibility Checker
A small business owner fills in their details:
- Annual income and loan amount
- GST filing compliance history
- Cash flow ratio
- Business revenue growth

The system instantly returns:
- **Risk score** (0-100%)
- **Decision** — Approved / Under Review / Rejected
- **AI-generated assessment letter** explaining the decision in plain English, signed by AltScore AI Agent

### 💬 Loan Officer Chatbot
A text-to-SQL chatbot where loan officers ask questions in plain English:

```
User:  "How many SME applicants defaulted?"
Bot:   Generates SQL → Queries PostgreSQL → Returns plain English answer

User:  "What is the average GST compliance for defaulters vs non-defaulters?"
Bot:   "Non-defaulters average 0.747 GST compliance vs 0.450 for defaulters"

User:  "Which income category has the highest default rate?"
Bot:   Queries live database → Returns instant answer
```

### 📊 Portfolio Dashboard
Live charts and metrics from the PostgreSQL database:
- Default rate by income category
- GST compliance comparison (defaulters vs non-defaulters)
- SME vs Non-SME default rate analysis

---

## 🏗️ System Architecture

```
Raw Data (Kaggle)
      ↓
Excel Profiling (5,000 rows)
      ↓
clean_data.py → application_cleaned.csv (307,511 rows)
      ↓
simulate_gst_data.py → gst_data.csv (alternative credit signals)
      ↓
load_to_db.py → PostgreSQL (4 tables, star schema)
      ↓
02_feature_engineering.ipynb → 29 engineered features
      ↓
03_model_training.ipynb → XGBoost + SHAP + MLflow
      ↓
┌─────────────────────────────────────────────┐
│           LLM Layer (Groq API)              │
│  rejection_letter.py + sql_chatbot.py       │
└─────────────────────────────────────────────┘
      ↓
FastAPI (REST endpoints: /score, /chat, /health)
      ↓
Streamlit Web App (4 pages)
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Data cleaning | Python + Pandas | 307,511 rows, 7 functions |
| Data simulation | NumPy + Faker | GST alternative signals |
| Database | PostgreSQL 18 | Star schema, 4 tables |
| Feature engineering | Pandas + Scikit-learn | 29 engineered features |
| ML Model | XGBoost | Credit risk classification |
| Explainability | SHAP | Feature importance + waterfall charts |
| Experiment tracking | MLflow | Model versioning + metrics |
| LLM | Groq API (Llama 3.3 70B) | Rejection letters + text-to-SQL |
| API | FastAPI | REST endpoints |
| Web App | Streamlit | 4-page interactive application |
| Excel | Microsoft Excel | Data profiling + IF formulas |

---

## 📊 Key Results

| Metric | Value |
|--------|-------|
| Dataset size | 307,511 applicants, 122 features |
| SME applicants identified | 71,627 (23.3%) |
| Features engineered | 29 custom features |
| Model AUC score | 0.9999 |
| Top feature | GST_RISK_SCORE (our engineered feature) |
| GST compliance — non-defaulters | 0.747 |
| GST compliance — defaulters | 0.450 |
| SME default rate | 7.48% |
| Non-SME default rate | 8.25% |
| API endpoints | 3 (/score, /chat, /health) |
| Chatbot accuracy | 3/3 test questions correct |

---

## 📁 Project Structure

```
altscore-sme-credit-engine/
│
├── data/
│   ├── raw/              ← Kaggle dataset (not committed)
│   ├── processed/        ← Cleaned CSV files
│   ├── simulated/        ← GST simulation data
│   └── README.md         ← Data documentation
│
├── notebooks/
│   ├── 01_eda.ipynb                  ← Exploratory analysis
│   ├── 02_feature_engineering.ipynb  ← 29 features built
│   └── 03_model_training.ipynb       ← XGBoost + SHAP + MLflow
│
├── src/
│   ├── data/
│   │   ├── clean_data.py          ← 7-function cleaning pipeline
│   │   ├── simulate_gst_data.py   ← Synthetic GST generation
│   │   └── load_to_db.py          ← PostgreSQL loading
│   ├── llm/
│   │   ├── rejection_letter.py    ← AI letter generator
│   │   └── sql_chatbot.py         ← Text-to-SQL chatbot
│   └── api/
│       └── main.py                ← FastAPI endpoints
│
├── models/
│   ├── xgboost_altscore.pkl   ← Trained model
│   ├── feature_names.pkl      ← Feature list
│   └── README.md              ← Model documentation
│
├── database/
│   ├── schema.sql   ← Full star schema SQL
│   └── README.md    ← Database documentation
│
├── reports/
│   └── figures/     ← All charts and plots
│
├── streamlit_app.py   ← Full web application
├── .env.example       ← Environment variables template
├── requirements.txt   ← Python dependencies
└── README.md          ← This file
```

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.12
- PostgreSQL 18
- Groq API key (free at console.groq.com)

### Step 1 — Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/altscore-sme-credit-engine.git
cd altscore-sme-credit-engine
```

### Step 2 — Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux
pip install -r requirements.txt
```

### Step 3 — Set up environment variables
```bash
cp .env.example .env
# Edit .env with your credentials
```

### Step 4 — Download dataset
```
Visit: https://www.kaggle.com/datasets/mishra5001/credit-card
Place CSV files in: data/raw/
```

### Step 5 — Run the pipeline
```bash
# Clean data
python src/data/clean_data.py

# Generate GST simulation
python src/data/simulate_gst_data.py

# Set up database
psql -U postgres -c "CREATE DATABASE altscore_db;"
python src/data/load_to_db.py

# Run notebooks in order
jupyter notebook
```

### Step 6 — Launch the web app
```bash
streamlit run streamlit_app.py
```

### Step 7 — Launch the API
```bash
python src/api/main.py
# Visit: http://127.0.0.1:8000/docs
```

---

## 🔍 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Check API status |
| POST | /score | Score a loan applicant |
| POST | /chat | Ask a question about the data |

### Example — Score an applicant
```bash
curl -X POST http://127.0.0.1:8000/score \
  -H "Content-Type: application/json" \
  -d '{"GST_RISK_SCORE": 0.8, "CASH_FLOW_RATIO": 1.5}'
```

Response:
```json
{
  "risk_score_pct": 12.45,
  "risk_tier": "Low Risk",
  "action": "Approve",
  "model_version": "xgboost-v1"
}
```

### Example — Ask the chatbot
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How many SME applicants defaulted?"}'
```

Response:
```json
{
  "question": "How many SME applicants defaulted?",
  "sql": "SELECT COUNT(*) FROM fact_loan_applications f JOIN dim_business b...",
  "answer": "There are 5,360 SME applicants who defaulted on their loans."
}
```

---

## 🧠 ML Model Details

### Feature Engineering
12 custom features engineered on top of 17 raw features:

| Feature | Formula | Category |
|---------|---------|----------|
| GST_RISK_SCORE | compliance×0.4 + streak×0.3 + penalty×0.3 | Alternative credit |
| CASHFLOW_STABILITY | cash_flow × gst_compliance | Alternative credit |
| CREDIT_EXT_INTERACTION | credit_ratio × (1 - ext_score) | Risk interaction |
| EXT_SOURCE_WEIGHTED | EXT1×0.25 + EXT2×0.45 + EXT3×0.30 | Bureau score |

### SHAP Explainability
Every prediction comes with a waterfall chart showing exactly which features drove the decision.

```
Good borrower  → 28.59% default probability → Approved
Bad borrower   → 71.37% default probability → Rejected
```

### MLflow Tracking
All experiments tracked at: `notebooks/mlflow.db`
```bash
mlflow ui --backend-store-uri sqlite:///notebooks/mlflow.db --host 127.0.0.1
```

---

## 💬 Chatbot Examples

```
Question: "How many SME applicants are in the database?"
Answer:   "There are 71,627 SME applicants in the database."

Question: "What is the average GST compliance for defaulters?"
Answer:   "Defaulters average 0.450 GST compliance vs 0.747 for non-defaulters."

Question: "How many high risk applicants have cash flow below 1?"
Answer:   "There are 1,215 high-risk applicants with cash flow ratio below 1."
```

---

## 📈 Reports and Figures

All charts saved in `reports/figures/`:

| Chart | Description |
|-------|-------------|
| correlation_plot.png | Feature correlations with TARGET |
| engineered_features.png | Distribution of engineered features |
| roc_curve.png | XGBoost ROC curve (AUC 0.9999) |
| feature_importance.png | XGBoost feature importance |
| shap_summary.png | SHAP mean absolute impact |
| shap_waterfall.png | Good borrower explanation |
| shap_waterfall_defaulter.png | High risk borrower explanation |

---

## 🎓 Academic Context

**Program:** Master of Science in Big Data Analytics
**Semester:** 4 (Capstone Project)
**Target Role:** AI Engineer
**Domain:** Indian Fintech / Banking

---

## 👤 Author

**Pranav**
MS Big Data Analytics — Semester 4
GitHub: github.com/YOUR_USERNAME

---

*Built with Python, PostgreSQL, XGBoost, SHAP, Groq LLM, FastAPI and Streamlit*
*April 2026*
