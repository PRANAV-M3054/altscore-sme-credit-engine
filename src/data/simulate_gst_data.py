import pandas as pd
import numpy as np
import os

np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLEANED_FILE = os.path.join(BASE_DIR, "data", "processed", "application_cleaned.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "simulated", "gst_data.csv")


def load_cleaned_data(filepath):
    print("Loading cleaned data...")
    df = pd.read_csv(filepath)
    print("Shape:", df.shape)
    print("SME applicants:", df['IS_SME'].sum())
    return df[['SK_ID_CURR', 'TARGET', 'IS_SME', 'AMT_INCOME_TOTAL']]




def generate_gst_features(df):
    print("Generating GST features...")
    n = len(df)

    # Base compliance score — linked to TARGET
    # Non-defaulters (TARGET=0) get higher compliance
    # Defaulters (TARGET=1) get lower compliance
    base_compliance = np.where(df['TARGET'] == 0, 0.75, 0.45)

    # Add random noise so it doesn't look fake
    noise = np.random.normal(0, 0.15, n)
    compliance = (base_compliance + noise).clip(0, 1).round(2)

    # GST registered — SME applicants more likely to be registered
    gst_registered = np.where(df['IS_SME'] == 1,
                               np.random.choice([0, 1], n, p=[0.1, 0.9]),
                               np.random.choice([0, 1], n, p=[0.4, 0.6]))

    # Quarterly turnover — based on income level
    base_turnover = df['AMT_INCOME_TOTAL'] * np.random.uniform(0.8, 2.5, n)
    turnover = base_turnover.round(0)

    # Turnover growth — defaulters tend to have negative growth
    base_growth = np.where(df['TARGET'] == 0,
                            np.random.uniform(0.0, 0.3, n),
                            np.random.uniform(-0.3, 0.1, n))
    growth = base_growth.round(3)

    # Filing streak — consecutive quarters filed on time (0 to 8)
    base_streak = np.where(df['TARGET'] == 0,
                            np.random.randint(4, 9, n),
                            np.random.randint(0, 5, n))

    # Cash flow ratio — inflow vs outflow
    base_cashflow = np.where(df['TARGET'] == 0,
                              np.random.uniform(1.1, 2.0, n),
                              np.random.uniform(0.5, 1.2, n))
    cashflow = base_cashflow.round(2)

    # Penalty count — late filing penalties
    base_penalty = np.where(df['TARGET'] == 0,
                             np.random.randint(0, 2, n),
                             np.random.randint(1, 6, n))

    # Build the output dataframe
    gst_df = pd.DataFrame({
        'SK_ID_CURR'           : df['SK_ID_CURR'].values,
        'GST_REGISTERED'       : gst_registered,
        'GST_FILING_COMPLIANCE': compliance,
        'GST_QUARTERLY_TURNOVER': turnover,
        'GST_TURNOVER_GROWTH'  : growth,
        'GST_FILING_STREAK'    : base_streak,
        'CASH_FLOW_RATIO'      : cashflow,
        'GST_PENALTY_COUNT'    : base_penalty
    })

    print("GST dataframe shape:", gst_df.shape)
    print("\nSample output:")
    print(gst_df.head())
    return gst_df


def validate_gst_data(gst_df, df):
    print("\nValidation — comparing defaulters vs non-defaulters:")
    
    # Merge GST data with TARGET column
    merged = gst_df.merge(df[['SK_ID_CURR', 'TARGET']], on='SK_ID_CURR')
    
    # Group by TARGET and calculate averages
    summary = merged.groupby('TARGET')[[
        'GST_FILING_COMPLIANCE',
        'GST_FILING_STREAK',
        'CASH_FLOW_RATIO',
        'GST_PENALTY_COUNT'
    ]].mean().round(3)
    
    print(summary)
    print("\nTARGET 0 = non-defaulter, TARGET 1 = defaulter")
    return merged

df = load_cleaned_data(CLEANED_FILE)
gst_df = generate_gst_features(df)
validate_gst_data(gst_df, df)


def save_gst_data(gst_df, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    gst_df.to_csv(filepath, index=False)
    file_size = os.path.getsize(filepath) / (1024 * 1024)
    print(f"\nSaved GST data to: {filepath}")
    print(f"Shape: {gst_df.shape}")
    print(f"File size: {round(file_size, 1)} MB")
    
    
def main():
    print("=" * 50)
    print("AltScore — GST Data Simulation")
    print("=" * 50)

    df = load_cleaned_data(CLEANED_FILE)
    gst_df = generate_gst_features(df)
    validate_gst_data(gst_df, df)
    save_gst_data(gst_df, OUTPUT_FILE)

    print("=" * 50)
    print("GST simulation complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()