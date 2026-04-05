# ⚡ API Layer — AltScore SME Credit Engine

> FastAPI REST endpoints serving the XGBoost model, SHAP explanations,
> and LLM-powered text-to-SQL chatbot.

---

## 📁 Files in This Directory

```
src/api/
├── main.py    ← FastAPI application with all endpoints
└── README.md  ← This file
```

---

## 🚀 Quick Start

```bash
# From project root
python src/api/main.py

# Visit interactive docs
http://127.0.0.1:8000/docs
```

---

## 📡 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check API status |
| POST | `/score` | Score a loan applicant |
| POST | `/chat` | Ask a question in plain English |

---

## 🔍 Endpoint Details

### GET /health
Check if the API is running.

**Response:**
```json
{
  "status": "running",
  "model": "XGBoost AltScore v1",
  "features": 29,
  "message": "AltScore API is live!"
}
```

---

### POST /score
Submit applicant data and receive a risk score and loan decision.

**Request body** — 29 features with default values pre-filled:
```json
{
  "EXT_SOURCE_1": 0.5,
  "EXT_SOURCE_2": 0.5,
  "GST_RISK_SCORE": 0.7,
  "CASH_FLOW_RATIO": 1.2,
  "CREDIT_TO_INCOME_RATIO": 4.0,
  "IS_SME": 1.0
}
```

**Response:**
```json
{
  "risk_score_pct": 28.59,
  "risk_tier": "Low Risk",
  "action": "Approve",
  "model_version": "xgboost-v1"
}
```

**Risk tiers:**

| Score | Tier | Action |
|-------|------|--------|
| 0% — 30% | Low Risk | Approve |
| 30% — 60% | Medium Risk | Review |
| 60% — 100% | High Risk | Reject |

---

### POST /chat
Ask any question about the loan portfolio in plain English.
The API generates SQL, queries PostgreSQL, and returns a plain English answer.

**Request body:**
```json
{
  "question": "How many SME applicants are in the database?"
}
```

**Response:**
```json
{
  "question": "How many SME applicants are in the database?",
  "sql": "SELECT COUNT(*) FROM dim_business WHERE \"IS_SME\" = 1 LIMIT 20",
  "data": [{"count": 71627}],
  "answer": "There are 71,627 SME applicants in the database."
}
```

**Example questions you can ask:**
- "What is the average GST compliance for defaulters vs non-defaulters?"
- "How many high risk applicants have cash flow ratio below 1?"
- "Which income category has the highest default rate?"
- "How many SME applicants defaulted?"

---

## 🏗️ How It Works

```
POST /score
    ↓
ApplicantInput (Pydantic model validates data)
    ↓
pandas DataFrame (29 features in correct order)
    ↓
XGBoost model.predict_proba()
    ↓
Risk score + tier + action returned as JSON

POST /chat
    ↓
ChatInput (question string)
    ↓
Groq LLM generates SQL from question + schema context
    ↓
SQLAlchemy executes SQL against PostgreSQL
    ↓
Groq LLM converts results to plain English
    ↓
Question + SQL + data + answer returned as JSON
```

---

## ⚙️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI |
| Server | Uvicorn |
| Data validation | Pydantic |
| ML model | XGBoost (loaded from pickle) |
| Database | PostgreSQL via SQLAlchemy |
| LLM | Groq API (Llama 3.3 70B) |

---

## 🔑 Environment Variables Required

```
GROQ_API_KEY=your_groq_key
DB_HOST=localhost
DB_PORT=5432
DB_NAME=altscore_db
DB_USER=postgres
DB_PASSWORD=your_password
```

---

## 📖 Interactive Documentation

FastAPI auto-generates two documentation interfaces:

**Swagger UI** — interactive, test endpoints directly in browser:
```
http://127.0.0.1:8000/docs
```

**ReDoc** — clean reference documentation:
```
http://127.0.0.1:8000/redoc
```

---

## 🔗 How This Connects to the Full Pipeline

```
XGBoost model (models/xgboost_altscore.pkl)
        ↓
FastAPI /score endpoint
        ↓
Streamlit app (loan eligibility page)
        ↓
User sees risk score + AI letter

PostgreSQL (altscore_db)
        ↓
FastAPI /chat endpoint (Groq LLM → SQL)
        ↓
Streamlit app (chatbot page)
        ↓
Loan officer sees plain English answer
```

---

*API built: April 2026*
*Project: AltScore — SME Credit Intelligence Engine*
