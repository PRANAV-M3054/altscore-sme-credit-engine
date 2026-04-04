import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_rejection_letter(applicant_data, shap_factors):
    """
    Takes applicant data and top SHAP risk factors,
    generates a professional rejection letter using Groq LLM.
    
    applicant_data : dict with applicant details
    shap_factors   : list of top 3 negative SHAP features
    """

    prompt = f"""
You are a senior loan officer at an Indian bank writing a formal but empathetic 
loan rejection letter for a small business owner.

Applicant Details:
- Business Type: {applicant_data['business_type']}
- Annual Income: Rs {applicant_data['annual_income']:,}
- Loan Amount Requested: Rs {applicant_data['loan_amount']:,}
- Credit-to-Income Ratio: {applicant_data['credit_ratio']}
- GST Filing Compliance: {applicant_data['gst_compliance']}
- Cash Flow Ratio: {applicant_data['cash_flow_ratio']}
- Risk Score: {applicant_data['risk_score']}%

Top 3 Risk Factors identified by our AI model:
1. {shap_factors[0]}
2. {shap_factors[1]}
3. {shap_factors[2]}

Write a professional rejection letter that:
1. Opens with a respectful greeting
2. States the loan application has been reviewed
3. Explains the rejection in simple business terms (no technical ML jargon)
4. Mentions 3 specific steps the applicant can take to improve eligibility
5. Ends with encouragement to reapply in 6 months
6. Keeps the tone empathetic and respectful
7. Is written for an Indian SME context

Keep the letter under 300 words.
"""

    message = client.chat.completions.create(
        model      = "llama-3.3-70b-versatile",
        messages   = [{"role": "user", "content": prompt}],
        max_tokens = 1024
    )

    return message.choices[0].message.content


# ── Test ─────────────────────────────────────────────────────
test_applicant = {
    'business_type'  : 'Self-employed retail trader',
    'annual_income'  : 180000,
    'loan_amount'    : 1440000,
    'credit_ratio'   : 8.0,
    'gst_compliance' : 0.42,
    'cash_flow_ratio': 0.78,
    'risk_score'     : 71.37
}

test_shap_factors = [
    "Low GST filing compliance (0.42) — filed on time only 42% of quarters",
    "Poor cash flow ratio (0.78) — more money going out than coming in",
    "High credit-to-income ratio (8.0) — borrowing 8x annual income"
]

print("Generating rejection letter...")
print("=" * 60)

letter = generate_rejection_letter(test_applicant, test_shap_factors)
print(letter)

print("=" * 60)
print("Letter generated successfully!")



def generate_shap_narrative(applicant_data, shap_factors, risk_score):
    """
    Converts SHAP values into a plain English explanation
    that a loan officer or applicant can understand.
    """

    prompt = f"""
You are an AI credit analyst explaining a loan risk assessment 
to a non-technical loan officer at an Indian bank.

Applicant risk score: {risk_score}%
Risk tier: {"High Risk" if risk_score > 60 else "Medium Risk" if risk_score > 30 else "Low Risk"}

The AI model identified these as the most important factors:
1. {shap_factors[0]}
2. {shap_factors[1]}
3. {shap_factors[2]}

Write a 3-4 sentence plain English explanation of:
- Why this applicant received this risk score
- Which factor is most concerning and why
- What this means for the loan decision

No technical jargon. Write as if explaining to a bank manager
who understands business but not machine learning.
"""

    message = client.chat.completions.create(
        model      = "llama-3.3-70b-versatile",
        messages   = [{"role": "user", "content": prompt}],
        max_tokens = 512
    )

    return message.choices[0].message.content


print("\nGenerating SHAP narrative...")
print("=" * 60)

narrative = generate_shap_narrative(
    test_applicant,
    test_shap_factors,
    risk_score = 71.37
)
print(narrative)
print("=" * 60)
print("Narrative generated successfully!")