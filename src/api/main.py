from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import pickle
import pandas as pd
import numpy as np
import shap
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from groq import Groq

load_dotenv()

# Get project root regardless of where script is run from
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with open(os.path.join(BASE_DIR, "models", "xgboost_altscore.pkl"), "rb") as f:
    model = pickle.load(f)

with open(os.path.join(BASE_DIR, "models", "feature_names.pkl"), "rb") as f:
    feature_names = pickle.load(f)

# ── Database connection ───────────────────────────────────
DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DB_URL)

# ── Groq client ───────────────────────────────────────────
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── FastAPI app ───────────────────────────────────────────
app = FastAPI(
    title       = "AltScore — SME Credit Intelligence Engine",
    description = "AI-powered alternative credit scoring for Indian SMEs",
    version     = "1.0.0"
)

@app.get("/health")
def health_check():
    return {
        "status"  : "running",
        "model"   : "XGBoost AltScore v1",
        "features": len(feature_names),
        "message" : "AltScore API is live!"
    }


class ApplicantInput(BaseModel):
    EXT_SOURCE_1              : float = 0.5
    EXT_SOURCE_2              : float = 0.5
    EXT_SOURCE_3              : float = 0.5
    EXT_SOURCE_MEAN           : float = 0.5
    EXT_SOURCE_MIN            : float = 0.5
    EXT_SOURCE_WEIGHTED       : float = 0.5
    CREDIT_TO_INCOME_RATIO    : float = 4.0
    ANNUITY_TO_INCOME_RATIO   : float = 0.3
    DEBT_SERVICE_RATIO        : float = 0.2
    LOAN_TO_GOODS_RATIO       : float = 1.0
    GST_RISK_SCORE            : float = 0.7
    GST_FILING_COMPLIANCE     : float = 0.7
    CASH_FLOW_RATIO           : float = 1.2
    CASHFLOW_STABILITY        : float = 1.0
    GST_TURNOVER_GROWTH       : float = 0.1
    GST_PENALTY_COUNT         : float = 0.0
    GST_FILING_STREAK         : float = 6.0
    GST_REGISTERED            : float = 1.0
    AGE_YEARS                 : float = 35.0
    YEARS_EMPLOYED            : float = 5.0
    AGE_EMPLOYMENT_RATIO      : float = 0.14
    INCOME_PER_FAMILY_MEMBER  : float = 50000.0
    IS_SME                    : float = 1.0
    HIGH_RISK_FLAG            : float = 0.0
    IS_STABLE_EMPLOYMENT      : float = 1.0
    SME_GST_COMBINED          : float = 0.7
    CREDIT_EXT_INTERACTION    : float = 2.0
    GST_GROWTH_COMPLIANCE     : float = 0.8
    REGION_RATING_CLIENT      : float = 2.0


class ChatInput(BaseModel):
    question: str
    

@app.post("/score")
def score_applicant(applicant: ApplicantInput):
    
    # Convert input to dataframe
    input_dict = applicant.model_dump()
    input_df = pd.DataFrame([input_dict])[feature_names]
    
    # Get risk score
    risk_score = model.predict_proba(input_df)[0][1]
    risk_score_pct = round(float(risk_score) * 100, 2)
    
    # Determine risk tier
    if risk_score < 0.30:
        tier   = "Low Risk"
        action = "Approve"
    elif risk_score < 0.60:
        tier   = "Medium Risk"
        action = "Review"
    else:
        tier   = "High Risk"
        action = "Reject"
    
    return {
        "risk_score_pct" : risk_score_pct,
        "risk_tier"      : tier,
        "action"         : action,
        "model_version"  : "xgboost-v1"
    }
    

@app.post("/chat")
def chat(input: ChatInput):
    
    question = input.question
    
    # Step 1 — Generate SQL
    db_schema = """
You have access to these PostgreSQL tables:
- fact_loan_applications: SK_ID_CURR, TARGET, AGE_YEARS, YEARS_EMPLOYED, EXT_SOURCE_1, EXT_SOURCE_2, EXT_SOURCE_3
- dim_business: SK_ID_CURR, NAME_INCOME_TYPE, IS_SME, INCOME_CATEGORY
- dim_cashflow: SK_ID_CURR, AMT_INCOME_TOTAL, AMT_CREDIT, CREDIT_TO_INCOME_RATIO, HIGH_RISK_FLAG
- dim_gst: SK_ID_CURR, GST_FILING_COMPLIANCE, CASH_FLOW_RATIO, GST_PENALTY_COUNT, GST_FILING_STREAK

CRITICAL RULES:
- Always use double quotes around column names e.g. "IS_SME"
- IS_SME, TARGET, HIGH_RISK_FLAG are INTEGER columns — use 1 or 0, NEVER TRUE or FALSE
- Always JOIN using ON f."SK_ID_CURR" = other_table."SK_ID_CURR"
- Add LIMIT 20 to every query
- Return ONLY the SQL query, nothing else, no explanation, no backticks
"""
    
    sql_prompt = f"{db_schema}\nConvert to SQL: {question}"
    
    sql_response = client.chat.completions.create(
        model      = "llama-3.3-70b-versatile",
        messages   = [{"role": "user", "content": sql_prompt}],
        max_tokens = 512
    )
    
    sql = sql_response.choices[0].message.content.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    
    # Step 2 — Run SQL
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            rows   = result.fetchall()
            cols   = list(result.keys())
            data   = [dict(zip(cols, row)) for row in rows]
    except Exception as e:
        return {"question": question, "sql": sql, "error": str(e)}
    
    # Step 3 — Generate answer
    answer_prompt = f"""
Question: {question}
Data: {data}
Write a 2-3 sentence plain English answer with key numbers.
"""
    
    answer_response = client.chat.completions.create(
        model      = "llama-3.3-70b-versatile",
        messages   = [{"role": "user", "content": answer_prompt}],
        max_tokens = 256
    )
    
    answer = answer_response.choices[0].message.content
    
    return {
        "question": question,
        "sql"     : sql,
        "data"    : data[:5],
        "answer"  : answer
    }
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host     = "127.0.0.1",
        port     = 8000,
        reload   = True
    )
    

    
    
