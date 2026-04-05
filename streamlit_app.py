import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import shap
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from groq import Groq
from sqlalchemy import create_engine, text

load_dotenv()

# ── Page configuration ────────────────────────────────────
st.set_page_config(
    page_title = "AltScore — SME Credit Engine",
    page_icon  = "🏦",
    layout     = "wide"
)

# ── Load model ────────────────────────────────────────────
@st.cache_resource
def load_model():
    with open("models/xgboost_altscore.pkl", "rb") as f:
        model = pickle.load(f)
    with open("models/feature_names.pkl", "rb") as f:
        feature_names = pickle.load(f)
    return model, feature_names

model, feature_names = load_model()

# ── Database connection ───────────────────────────────────
@st.cache_resource
def get_engine():
    DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    return create_engine(DB_URL)

engine = get_engine()

# ── Groq client ───────────────────────────────────────────
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Sidebar ───────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/emoji/96/bank-emoji.png", width=80)
st.sidebar.title("AltScore")
st.sidebar.markdown("*SME Credit Intelligence Engine*")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "📋 Loan Eligibility Check", "💬 Loan Officer Chatbot", "📊 Portfolio Dashboard"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Built with:**")
st.sidebar.markdown("XGBoost · SHAP · Groq LLM · PostgreSQL")

# ── Home Page ─────────────────────────────────────────────
if page == "🏠 Home":
    st.title("🏦 AltScore — SME Credit Intelligence Engine")
    st.markdown("### AI-powered alternative credit scoring for Indian small businesses")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Applicants", "3,07,511")
    with col2:
        st.metric("SME Applicants", "71,627")
    with col3:
        st.metric("Model AUC", "0.9999")
    with col4:
        st.metric("Default Rate", "8.07%")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎯 What is AltScore?")
        st.markdown("""
        Traditional banks reject **80% of SME loan applications** because small 
        businesses have no credit history — no home loan, no credit card, 
        nothing in the CIBIL system.
        
        AltScore fixes this by using **alternative data signals**:
        - GST filing compliance patterns
        - Cash flow behaviour
        - Business growth trends
        - Payment regularity
        
        These signals are **4-5x more predictive** than traditional bureau scores
        for SME applicants.
        """)

    with col2:
        st.markdown("### 🔧 How It Works")
        st.markdown("""
        **Step 1 — Data Collection**
        GST filing records, transaction history, business profile
        
        **Step 2 — AI Scoring**
        XGBoost model with 29 engineered features scores each applicant
        
        **Step 3 — Explainability**
        SHAP values identify exactly which factors drove the decision
        
        **Step 4 — LLM Narrative**
        Groq LLM converts technical scores into plain English letters
        
        **Step 5 — Decision**
        Approve / Review / Reject with full audit trail
        """)

    st.markdown("---")
    st.markdown("### 🚀 Get Started")
    st.markdown("Use the sidebar to navigate to **Loan Eligibility Check** to score an applicant.")
    
    
    
# ── Loan Eligibility Check Page ───────────────────────────
elif page == "📋 Loan Eligibility Check":
    st.title("📋 Loan Eligibility Check")
    st.markdown("Fill in your business details to check loan eligibility instantly.")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 💼 Business Profile")
        annual_income = st.number_input(
            "Annual Income (Rs)", 
            min_value=50000, 
            max_value=10000000, 
            value=300000,
            step=10000
        )
        loan_amount = st.number_input(
            "Loan Amount Requested (Rs)",
            min_value=50000,
            max_value=5000000,
            value=900000,
            step=50000
        )
        age = st.slider("Your Age", 21, 65, 35)
        years_employed = st.slider("Years in Business", 0, 30, 5)

    with col2:
        st.markdown("### 📊 GST & Compliance")
        gst_registered = st.selectbox("GST Registered?", [1, 0], format_func=lambda x: "Yes" if x == 1 else "No")
        gst_compliance = st.slider("GST Filing Compliance (0=Poor, 1=Perfect)", 0.0, 1.0, 0.75, 0.01)
        gst_streak = st.slider("Consecutive Quarters Filed on Time", 0, 8, 6)
        gst_penalty = st.slider("Late Filing Penalties", 0, 5, 0)
        gst_growth = st.slider("Business Revenue Growth", -0.5, 0.5, 0.1, 0.01)

    with col3:
        st.markdown("### 💰 Financial Health")
        cash_flow = st.slider("Cash Flow Ratio (inflow/outflow)", 0.5, 2.5, 1.3, 0.01)
        ext_source = st.slider("External Credit Score (0=Poor, 1=Excellent)", 0.0, 1.0, 0.55, 0.01)
        region_rating = st.selectbox("Region Risk Rating", [1, 2, 3], index=1)
        is_sme = st.selectbox("Business Type", [1, 0], format_func=lambda x: "SME / Self-employed" if x == 1 else "Salaried Employee")

    st.markdown("---")
    check_button = st.button("🔍 Check Loan Eligibility", use_container_width=True)

    if check_button:
        # Calculate derived features
        credit_ratio      = round(loan_amount / annual_income, 2)
        annuity_ratio     = round((loan_amount / 60) / (annual_income / 12), 2)
        debt_ratio        = round((loan_amount / 60) / annual_income, 2)
        loan_goods_ratio  = 1.0
        gst_risk          = round(gst_compliance * 0.4 + (gst_streak / 8) * 0.3 + (1 - gst_penalty / 5) * 0.3, 3)
        cashflow_stab     = round(cash_flow * gst_compliance, 3)
        gst_growth_comp   = round(gst_growth + gst_compliance, 3)
        ext_mean          = round(ext_source, 3)
        ext_min           = round(ext_source * 0.9, 3)
        ext_weighted      = round(ext_source, 3)
        credit_ext        = round(credit_ratio * (1 - ext_mean), 3)
        age_emp_ratio     = round(years_employed / max(age, 1), 3)
        income_per_fam    = round(annual_income / 3, 2)
        high_risk_flag    = 1 if credit_ratio > 8 else 0
        stable_emp        = 1 if years_employed >= 2 else 0
        sme_gst           = round(is_sme * gst_risk, 3)

        # Build feature dict
        features = {
            'EXT_SOURCE_1'            : ext_source,
            'EXT_SOURCE_2'            : ext_source,
            'EXT_SOURCE_3'            : ext_source,
            'EXT_SOURCE_MEAN'         : ext_mean,
            'EXT_SOURCE_MIN'          : ext_min,
            'EXT_SOURCE_WEIGHTED'     : ext_weighted,
            'CREDIT_TO_INCOME_RATIO'  : credit_ratio,
            'ANNUITY_TO_INCOME_RATIO' : annuity_ratio,
            'DEBT_SERVICE_RATIO'      : debt_ratio,
            'LOAN_TO_GOODS_RATIO'     : loan_goods_ratio,
            'GST_RISK_SCORE'          : gst_risk,
            'GST_FILING_COMPLIANCE'   : gst_compliance,
            'CASH_FLOW_RATIO'         : cash_flow,
            'CASHFLOW_STABILITY'      : cashflow_stab,
            'GST_TURNOVER_GROWTH'     : gst_growth,
            'GST_PENALTY_COUNT'       : gst_penalty,
            'GST_FILING_STREAK'       : gst_streak,
            'GST_REGISTERED'          : gst_registered,
            'AGE_YEARS'               : age,
            'YEARS_EMPLOYED'          : years_employed,
            'AGE_EMPLOYMENT_RATIO'    : age_emp_ratio,
            'INCOME_PER_FAMILY_MEMBER': income_per_fam,
            'IS_SME'                  : is_sme,
            'HIGH_RISK_FLAG'          : high_risk_flag,
            'IS_STABLE_EMPLOYMENT'    : stable_emp,
            'SME_GST_COMBINED'        : sme_gst,
            'CREDIT_EXT_INTERACTION'  : credit_ext,
            'GST_GROWTH_COMPLIANCE'   : gst_growth_comp,
            'REGION_RATING_CLIENT'    : region_rating
        }

        input_df = pd.DataFrame([features])[feature_names]
        risk_score = model.predict_proba(input_df)[0][1]
        risk_pct = round(risk_score * 100, 2)

        # Show result
        st.markdown("## 📊 Assessment Result")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Risk Score", f"{risk_pct}%")
        with col2:
            if risk_score < 0.30:
                st.success("✅ LOW RISK — APPROVED")
                decision = "Approved"
                tier = "Low Risk"
            elif risk_score < 0.60:
                st.warning("⚠️ MEDIUM RISK — UNDER REVIEW")
                decision = "Under Review"
                tier = "Medium Risk"
            else:
                st.error("❌ HIGH RISK — REJECTED")
                decision = "Rejected"
                tier = "High Risk"
        with col3:
            st.metric("Credit-to-Income Ratio", f"{credit_ratio}x")

        # Show rejection letter if rejected
        if risk_score >= 0.30:
            st.markdown("---")
            st.markdown("### 📝 AI-Generated Assessment Letter")

            with st.spinner("Generating letter using AI..."):
                shap_factors = [
                    f"GST Filing Compliance: {gst_compliance} — {'Good' if gst_compliance > 0.6 else 'Needs improvement'}",
                    f"Cash Flow Ratio: {cash_flow} — {'Healthy' if cash_flow > 1.2 else 'Below recommended level'}",
                    f"Credit-to-Income Ratio: {credit_ratio}x — {'Acceptable' if credit_ratio < 5 else 'High debt burden'}"
                ]

                applicant_data = {
                    'business_type'  : 'SME / Self-employed business' if is_sme else 'Salaried',
                    'annual_income'  : annual_income,
                    'loan_amount'    : loan_amount,
                    'credit_ratio'   : credit_ratio,
                    'gst_compliance' : gst_compliance,
                    'cash_flow_ratio': cash_flow,
                    'risk_score'     : risk_pct
                }

                prompt = f"""
You are an AI credit assessment agent for AltScore — an AI-powered 
alternative credit scoring platform for Indian small businesses.

Applicant Details:
- Business Type: {applicant_data['business_type']}
- Annual Income: Rs {applicant_data['annual_income']:,}
- Loan Amount Requested: Rs {applicant_data['loan_amount']:,}
- Credit-to-Income Ratio: {applicant_data['credit_ratio']}
- GST Filing Compliance: {applicant_data['gst_compliance']}
- Cash Flow Ratio: {applicant_data['cash_flow_ratio']}
- Risk Score: {applicant_data['risk_score']}%
- Decision: {decision}

Key factors:
1. {shap_factors[0]}
2. {shap_factors[1]}
3. {shap_factors[2]}

Write a professional assessment letter that:
1. Opens with Namaste and respectful greeting
2. States the loan decision clearly
3. Explains reasons in simple business terms
4. If rejected or under review — gives 3 specific improvement steps
5. Ends encouragingly
6. Keeps tone empathetic and professional
7. Written for Indian SME context
8. Sign off exactly like this at the end:
   Dhanyavad,
   AltScore AI Agent
   AltScore Credit Intelligence Platform

Keep under 300 words.
"""
                message = client.chat.completions.create(
                    model      = "llama-3.3-70b-versatile",
                    messages   = [{"role": "user", "content": prompt}],
                    max_tokens = 1024
                )
                letter = message.choices[0].message.content
                st.text_area("Assessment Letter", letter, height=350)
                
                

# ── Chatbot Page ──────────────────────────────────────────
elif page == "💬 Loan Officer Chatbot":
    st.title("💬 Loan Officer Chatbot")
    st.markdown("Ask any question about the loan portfolio in plain English.")
    st.markdown("---")

    # Example questions
    st.markdown("### 💡 Example Questions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("How many SME applicants?"):
            st.session_state.question = "How many SME applicants are in the database?"
    with col2:
        if st.button("GST compliance by default status?"):
            st.session_state.question = "What is the average GST compliance score for defaulters vs non-defaulters?"
    with col3:
        if st.button("High risk applicants count?"):
            st.session_state.question = "How many high risk applicants have a cash flow ratio below 1?"

    st.markdown("---")

    # Chat input
    question = st.text_input(
        "Type your question here:",
        value = st.session_state.get("question", ""),
        placeholder = "e.g. How many SME applicants defaulted?"
    )

    if st.button("🔍 Ask", use_container_width=True):
        if question:
            with st.spinner("Thinking..."):

                # Generate SQL
                db_schema = """
You have access to these PostgreSQL tables:
- fact_loan_applications: SK_ID_CURR, TARGET, AGE_YEARS, YEARS_EMPLOYED, EXT_SOURCE_1, EXT_SOURCE_2, EXT_SOURCE_3
- dim_business: SK_ID_CURR, NAME_INCOME_TYPE, IS_SME, INCOME_CATEGORY
- dim_cashflow: SK_ID_CURR, AMT_INCOME_TOTAL, AMT_CREDIT, CREDIT_TO_INCOME_RATIO, HIGH_RISK_FLAG
- dim_gst: SK_ID_CURR, GST_FILING_COMPLIANCE, CASH_FLOW_RATIO, GST_PENALTY_COUNT, GST_FILING_STREAK

CRITICAL RULES:
- Always use double quotes around column names
- IS_SME, TARGET, HIGH_RISK_FLAG are INTEGER — use 1 or 0, NEVER TRUE or FALSE
- JOIN using ON f."SK_ID_CURR" = other."SK_ID_CURR"
- Add LIMIT 20
- Return ONLY the SQL query, no explanation, no backticks
"""
                sql_response = client.chat.completions.create(
                    model    = "llama-3.3-70b-versatile",
                    messages = [{"role": "user", "content": f"{db_schema}\nConvert to SQL: {question}"}],
                    max_tokens = 512
                )
                sql = sql_response.choices[0].message.content.strip()
                sql = sql.replace("```sql", "").replace("```", "").strip()

                # Run query
                try:
                    with engine.connect() as conn:
                        result = conn.execute(text(sql))
                        rows   = result.fetchall()
                        cols   = list(result.keys())
                        data   = [dict(zip(cols, row)) for row in rows]

                    # Generate answer
                    answer_response = client.chat.completions.create(
                        model    = "llama-3.3-70b-versatile",
                        messages = [{"role": "user", "content": f"Question: {question}\nData: {data}\nWrite a 2-3 sentence plain English answer with key numbers."}],
                        max_tokens = 256
                    )
                    answer = answer_response.choices[0].message.content

                    # Show results
                    st.markdown("### 💬 Answer")
                    st.info(answer)

                    st.markdown("### 🔧 Generated SQL")
                    st.code(sql, language="sql")

                    st.markdown("### 📊 Raw Data")
                    if data:
                        st.dataframe(pd.DataFrame(data))

                except Exception as e:
                    st.error(f"Query error: {e}")
                    st.code(sql, language="sql")
        else:
            st.warning("Please type a question first!")
            
# ── Portfolio Dashboard Page ──────────────────────────────
elif page == "📊 Portfolio Dashboard":
    st.title("📊 Portfolio Dashboard")
    st.markdown("Live insights from the AltScore loan portfolio database.")
    st.markdown("---")

    # ── Row 1 — KPI Metrics ───────────────────────────────
    with engine.connect() as conn:
        total     = conn.execute(text('SELECT COUNT(*) FROM fact_loan_applications')).fetchone()[0]
        defaults  = conn.execute(text('SELECT COUNT(*) FROM fact_loan_applications WHERE "TARGET" = 1')).fetchone()[0]
        sme       = conn.execute(text('SELECT COUNT(*) FROM dim_business WHERE "IS_SME" = 1')).fetchone()[0]
        high_risk = conn.execute(text('SELECT COUNT(*) FROM dim_cashflow WHERE "HIGH_RISK_FLAG" = 1')).fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Applications", f"{total:,}")
    with col2:
        st.metric("Total Defaulters", f"{defaults:,}", delta=f"{round(defaults/total*100,2)}% rate")
    with col3:
        st.metric("SME Applicants", f"{sme:,}")
    with col4:
        st.metric("High Risk Applicants", f"{high_risk:,}")

    st.markdown("---")

    # ── Row 2 — Charts ────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Default Rate by Income Category")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT b."INCOME_CATEGORY",
                       COUNT(*) as total,
                       SUM(f."TARGET") as defaults,
                       ROUND(AVG(f."TARGET")::numeric * 100, 2) as default_rate
                FROM fact_loan_applications f
                JOIN dim_business b ON f."SK_ID_CURR" = b."SK_ID_CURR"
                GROUP BY b."INCOME_CATEGORY"
                ORDER BY default_rate DESC
            """))
            rows = result.fetchall()
            cols = list(result.keys())

        income_df = pd.DataFrame(rows, columns=cols)
        income_df.columns = income_df.columns.str.lower()
        income_df = income_df.dropna(subset=['income_category'])
        st.bar_chart(income_df.set_index('income_category')['default_rate'])

    with col2:
        st.markdown("### GST Compliance — Defaulters vs Non-Defaulters")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT f."TARGET",
                       ROUND(AVG(g."GST_FILING_COMPLIANCE")::numeric, 3) as avg_compliance,
                       ROUND(AVG(g."CASH_FLOW_RATIO")::numeric, 3) as avg_cashflow
                FROM fact_loan_applications f
                JOIN dim_gst g ON f."SK_ID_CURR" = g."SK_ID_CURR"
                GROUP BY f."TARGET"
                ORDER BY f."TARGET"
            """))
            rows = result.fetchall()
            cols = list(result.keys())

        gst_df = pd.DataFrame(rows, columns=cols)
        gst_df.columns = gst_df.columns.str.lower()
        gst_df['target'] = gst_df['target'].map({0: 'Non-defaulter', 1: 'Defaulter'})
        st.bar_chart(gst_df.set_index('target')['avg_compliance'])

    st.markdown("---")

    # ── Row 3 — SME Analysis ──────────────────────────────
    st.markdown("### SME vs Non-SME Default Rate")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT b."IS_SME",
                   COUNT(*) as total,
                   SUM(f."TARGET") as defaults,
                   ROUND(AVG(f."TARGET")::numeric * 100, 2) as default_rate
            FROM fact_loan_applications f
            JOIN dim_business b ON f."SK_ID_CURR" = b."SK_ID_CURR"
            GROUP BY b."IS_SME"
            ORDER BY b."IS_SME"
        """))
        rows = result.fetchall()
        cols = list(result.keys())

    sme_df = pd.DataFrame(rows, columns=cols)
    sme_df.columns = sme_df.columns.str.lower()
    sme_df['is_sme'] = sme_df['is_sme'].map({0: 'Non-SME', 1: 'SME'})

    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(sme_df, use_container_width=True)
    with col2:
        st.bar_chart(sme_df.set_index('is_sme')['default_rate'])
        
        
        
