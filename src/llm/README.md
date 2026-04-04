# 🤖 LLM Layer — AltScore SME Credit Engine

> AI-powered narrative generation and intelligent querying using Groq API (Llama 3.3 70B).
> Transforms raw ML predictions into human-readable insights for loan officers and applicants.

---

## 📁 Files in This Directory

```
src/llm/
├── rejection_letter.py   ← Generates RBI-compliant rejection letters
├── sql_chatbot.py        ← Text-to-SQL loan officer chatbot
└── README.md             ← This file
```

---

## 🧠 Why an LLM Layer?

Traditional ML models produce numbers — a risk score of 71.37% means nothing to a small business owner who just got rejected for a loan. The LLM layer bridges the gap between technical ML output and human understanding.

Three problems this layer solves:

| Problem | Solution |
|---------|----------|
| Applicants don't understand why they were rejected | Auto-generated rejection letter in plain English |
| Loan officers can't interpret SHAP waterfall charts | Plain English SHAP narrative explaining the decision |
| Querying data requires SQL knowledge | Text-to-SQL chatbot — ask questions in plain English |

---

## ⚙️ Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM Provider | Groq API |
| Model | Llama 3.3 70B Versatile |
| Database | PostgreSQL via SQLAlchemy |
| Environment | python-dotenv |

---

## 📄 rejection_letter.py

### What it does
Takes an applicant's financial profile and top 3 SHAP risk factors,
then generates a professional, empathetic loan rejection letter
written for the Indian SME context.

### How it works

```
Applicant data + SHAP factors
           ↓
    Structured prompt
           ↓
    Groq LLM API call
           ↓
  Professional rejection letter
```

### Example Input

```python
applicant_data = {
    'business_type'  : 'Self-employed retail trader',
    'annual_income'  : 180000,
    'loan_amount'    : 1440000,
    'credit_ratio'   : 8.0,
    'gst_compliance' : 0.42,
    'cash_flow_ratio': 0.78,
    'risk_score'     : 71.37
}

shap_factors = [
    "Low GST filing compliance (0.42) — filed on time only 42% of quarters",
    "Poor cash flow ratio (0.78) — more money going out than coming in",
    "High credit-to-income ratio (8.0) — borrowing 8x annual income"
]
```

### Example Output

```
Dear [Applicant's Name],

Namaste. I hope this letter finds you well. We appreciate the time 
you took to apply for a loan with our bank...

After careful consideration, I regret to inform you that we are 
unable to approve your loan request at this time. Our assessment 
indicates that your business's financial health is not currently 
stable enough to support the loan amount you have requested...

To improve your eligibility for a loan in the future, I would 
recommend the following steps:
1. Ensure that you file your GST returns on time, every time
2. Review your cash flow management to ensure stable positive flow
3. Consider reducing your debt obligations to a sustainable ratio

I encourage you to reapply in six months...

Sincerely,
Senior Loan Officer
```

### Two Functions

| Function | Input | Output |
|----------|-------|--------|
| `generate_rejection_letter(applicant_data, shap_factors)` | Dict + list | Rejection letter string |
| `generate_shap_narrative(applicant_data, shap_factors, risk_score)` | Dict + list + float | Plain English explanation |

### How to run
```bash
python src/llm/rejection_letter.py
```

---

## 💬 sql_chatbot.py

### What it does
A natural language interface to the PostgreSQL database.
Loan officers ask questions in plain English — the LLM converts
them to SQL, executes the query, and returns a plain English answer.

### How it works

```
Plain English question
        ↓
LLM generates SQL (with schema context)
        ↓
SQL executes against PostgreSQL
        ↓
Raw results passed back to LLM
        ↓
Plain English answer
```

### Three Functions

| Function | What it does |
|----------|-------------|
| `generate_sql(question)` | Converts plain English to PostgreSQL query |
| `run_query(sql)` | Executes SQL and returns formatted results |
| `generate_answer(question, result)` | Converts results to plain English |
| `ask(question)` | Full pipeline — calls all three above |

### Example Questions and Answers

**Question 1:**
```
How many SME applicants are in the database?
```
```
Generated SQL:
SELECT COUNT(f."SK_ID_CURR")
FROM fact_loan_applications f
JOIN dim_business d ON f."SK_ID_CURR" = d."SK_ID_CURR"
WHERE d."IS_SME" = 1

Answer:
There are 71,627 SME applicants in the database.
```

---

**Question 2:**
```
What is the average GST compliance score for defaulters vs non-defaulters?
```
```
Generated SQL:
SELECT f."TARGET", AVG(dg."GST_FILING_COMPLIANCE")
FROM fact_loan_applications f
JOIN dim_gst dg ON f."SK_ID_CURR" = dg."SK_ID_CURR"
GROUP BY f."TARGET"

Answer:
Non-defaulters average 0.747 GST compliance vs 0.450 for defaulters —
showing a strong correlation between GST compliance and loan repayment.
```

---

**Question 3:**
```
How many high risk applicants have a cash flow ratio below 1?
```
```
Generated SQL:
SELECT COUNT(*)
FROM fact_loan_applications f
JOIN dim_cashflow c ON f."SK_ID_CURR" = c."SK_ID_CURR"
JOIN dim_gst g ON f."SK_ID_CURR" = g."SK_ID_CURR"
WHERE c."HIGH_RISK_FLAG" = 1 AND g."CASH_FLOW_RATIO" < 1

Answer:
There are 1,215 high-risk applicants with cash flow ratio below 1,
meaning they spend more than they earn — significant repayment risk.
```

### How to run
```bash
python src/llm/sql_chatbot.py
```

---

## 🔑 Environment Variables Required

Add these to your `.env` file:

```
GROQ_API_KEY=your_groq_api_key_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=altscore_db
DB_USER=postgres
DB_PASSWORD=your_password
```

Get a free Groq API key at: https://console.groq.com

---

## 🔗 How This Connects to the Full Pipeline

```
XGBoost model
     ↓
Risk score + SHAP values
     ↓
rejection_letter.py  →  Rejection letter for applicant
     ↓
sql_chatbot.py       →  Loan officer Q&A interface
     ↓
FastAPI endpoints    →  REST API (Phase 7)
     ↓
Power BI dashboard   →  LLM insights panel (Phase 8)
```

---

## 💡 Why This Matters for RBI Compliance

Reserve Bank of India guidelines require banks to explain credit
decisions to applicants. Our LLM layer automates this requirement:

- Every rejection generates a plain English letter citing specific reasons
- SHAP values are converted to business language — no ML jargon
- Loan officers can query applicant data without writing SQL

This makes AltScore not just technically advanced but also
regulatory-ready for Indian banking deployment.

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| Avg letter generation time | ~3 seconds |
| Avg SQL generation time | ~2 seconds |
| Model | Llama 3.3 70B Versatile |
| API | Groq (free tier) |
| SQL accuracy | 3/3 test questions correct |

---

*LLM Layer built: April 2026*
*Project: AltScore — SME Credit Intelligence Engine*
