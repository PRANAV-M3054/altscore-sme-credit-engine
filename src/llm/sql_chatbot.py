import os
from dotenv import load_dotenv
from groq import Groq
from sqlalchemy import create_engine, text

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DB_URL)

# Database schema context — tells the LLM what tables exist
DB_SCHEMA = """
You have access to a PostgreSQL database with these tables:

1. fact_loan_applications
   - SK_ID_CURR (integer) — unique applicant ID
   - TARGET (integer) — 1=defaulted, 0=repaid
   - AGE_YEARS (float) — applicant age
   - YEARS_EMPLOYED (float) — years at current job
   - REGION_RATING_CLIENT (integer) — regional risk rating
   - EXT_SOURCE_1, EXT_SOURCE_2, EXT_SOURCE_3 (float) — credit bureau scores

2. dim_business
   - SK_ID_CURR (integer) — links to fact table
   - NAME_INCOME_TYPE (varchar) — employment type
   - NAME_EDUCATION_TYPE (varchar) — education level
   - ORGANIZATION_TYPE (varchar) — employer type
   - IS_SME (integer) — 1=SME applicant
   - INCOME_CATEGORY (varchar) — Low/Medium/High/Very High

3. dim_cashflow
   - SK_ID_CURR (integer) — links to fact table
   - AMT_INCOME_TOTAL (float) — annual income
   - AMT_CREDIT (float) — loan amount
   - CREDIT_TO_INCOME_RATIO (float) — credit/income ratio
   - HIGH_RISK_FLAG (integer) — 1=high risk
   - IS_STABLE_EMPLOYMENT (integer) — 1=stable

4. dim_gst
   - SK_ID_CURR (integer) — links to fact table
   - GST_FILING_COMPLIANCE (float) — compliance score 0-1
   - CASH_FLOW_RATIO (float) — inflow/outflow ratio
   - GST_PENALTY_COUNT (integer) — late filing penalties
   - GST_FILING_STREAK (integer) — consecutive on-time quarters

IMPORTANT RULES:
- Always use double quotes around column names e.g. "TARGET"
- Always use double quotes around table names if needed
- Use JOIN with ON f."SK_ID_CURR" = other."SK_ID_CURR"
- Always add LIMIT 100 to prevent large results
- Return ONLY the SQL query, nothing else, no explanation
"""


def generate_sql(question):
    """Convert plain English question to SQL query."""

    prompt = f"""
{DB_SCHEMA}

Convert this question to a PostgreSQL SQL query:
"{question}"

Return ONLY the SQL query. No explanation. No markdown. No backticks.
"""

    message = client.chat.completions.create(
        model      = "llama-3.3-70b-versatile",
        messages   = [{"role": "user", "content": prompt}],
        max_tokens = 512
    )

    sql = message.choices[0].message.content.strip()
    # Clean any markdown backticks if LLM adds them
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql


def run_query(sql):
    """Execute SQL query and return results as string."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = result.fetchall()
            columns = result.keys()

            if not rows:
                return "No results found."

            # Format as readable table
            output = " | ".join(columns) + "\n"
            output += "-" * 60 + "\n"
            for row in rows:
                output += " | ".join(str(val) for val in row) + "\n"

            return output
    except Exception as e:
        return f"Query error: {e}"


def generate_answer(question, query_result):
    """Convert raw SQL results to plain English answer."""

    prompt = f"""
A loan officer asked: "{question}"

The database returned:
{query_result}

Write a clear 2-3 sentence answer in plain English.
Include the key numbers from the results.
"""

    message = client.chat.completions.create(
        model      = "llama-3.3-70b-versatile",
        messages   = [{"role": "user", "content": prompt}],
        max_tokens = 256
    )

    return message.choices[0].message.content


def ask(question):
    """Full pipeline: question → SQL → results → plain English answer."""
    print(f"\nQuestion: {question}")
    print("-" * 60)

    sql = generate_sql(question)
    print(f"Generated SQL:\n{sql}\n")

    result = run_query(sql)
    print(f"Query result:\n{result}")

    answer = generate_answer(question, result)
    print(f"Answer: {answer}")
    print("=" * 60)
    
    
    
if __name__ == "__main__":
    print("AltScore SQL Chatbot")
    print("=" * 60)

    ask("How many SME applicants are in the database?")
    ask("What is the average GST compliance score for defaulters vs non-defaulters?")
    ask("How many high risk applicants have a cash flow ratio below 1?")