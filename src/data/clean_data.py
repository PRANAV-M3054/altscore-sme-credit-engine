import pandas as pd
import numpy as np
import os

INPUT_FILE = "data/raw/application_data.csv"
OUTPUT_FILE = "data/processed/application_cleaned.csv"

def load_data(file_path):
    df = pd.read_csv(file_path)
    print("Shape: ", df.shape)
    print("Rows: ", df.shape[0])
    print("Columns: ", df.shape[1])
    print("Default rate:",round(df['TARGET'].mean() * 100, 2), "%")
    print("Total defaulters:", df['TARGET'].sum())
    print("Total non-defaulters:", (df['TARGET'] == 0).sum())
    return df




def drop_high_missing(df, threshold=0.60):
    missing_pct = df.isnull().mean()
    cols_to_drop = missing_pct[missing_pct > threshold].index.tolist()
    print("Columns to drop:", len(cols_to_drop))
    df = df.drop(columns=cols_to_drop)
    print("Shape after dropping:", df.shape)
    return df




def fix_days_columns(df):
    df['DAYS_EMPLOYED'] = df['DAYS_EMPLOYED'].replace(365243, np.nan)
    print("Unemployed placeholder replaced with NaN")

    df['AGE_YEARS'] = (df['DAYS_BIRTH'] * -1 / 365).round(1)
    print("AGE_YEARS min:", df['AGE_YEARS'].min(), "max:", df['AGE_YEARS'].max())

    df['YEARS_EMPLOYED'] = (df['DAYS_EMPLOYED'] * -1 / 365).round(1)
    print("YEARS_EMPLOYED missing:", df['YEARS_EMPLOYED'].isna().sum())

    df = df.drop(columns=['DAYS_BIRTH', 'DAYS_EMPLOYED'])
    print("Shape after fixing days:", df.shape)
    return df





def impute_missing(df):
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categoric_cols = df.select_dtypes(include=['object']).columns

    for col in numeric_cols:
        if df[col].isna().sum() > 0:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)

    for col in categoric_cols:
        if df[col].isna().sum() > 0:
            mode_val = df[col].mode()[0]
            df[col] = df[col].fillna(mode_val)

    print("Missing values remaining:", df.isnull().sum().sum())
    return df





def cap_outliers(df):
    cols_to_cap = [
        'AMT_INCOME_TOTAL',
        'AMT_CREDIT',
        'AMT_ANNUITY',
        'AMT_GOODS_PRICE'
    ]

    for col in cols_to_cap:
        p99 = df[col].quantile(0.99)
        before_max = df[col].max()
        df[col] = df[col].clip(upper=p99)
        after_max = df[col].max()
        print(f"{col} — before max: {before_max:,.0f} → after max: {after_max:,.0f}")

    return df






def engineer_base_features(df):
    # Feature 1 — credit to income ratio
    df['CREDIT_TO_INCOME_RATIO'] = (df['AMT_CREDIT'] / df['AMT_INCOME_TOTAL']).round(2)
    print("CREDIT_TO_INCOME_RATIO — max:", df['CREDIT_TO_INCOME_RATIO'].max())

    # Feature 2 — annuity to income ratio
    df['ANNUITY_TO_INCOME_RATIO'] = (df['AMT_ANNUITY'] / (df['AMT_INCOME_TOTAL'] / 12)).round(2)
    print("ANNUITY_TO_INCOME_RATIO — max:", df['ANNUITY_TO_INCOME_RATIO'].max())

    # Feature 3 — IS_SME flag
    sme_types = ['Self-employed', 'Businessman', 'Commercial associate']
    df['IS_SME'] = df['NAME_INCOME_TYPE'].isin(sme_types).astype(int)
    print("SME applicants:", df['IS_SME'].sum())

    # Feature 4 — income category
    df['INCOME_CATEGORY'] = pd.cut(
        df['AMT_INCOME_TOTAL'],
        bins   = [0, 100000, 200000, 500000, float('inf')],
        labels = ['Low', 'Medium', 'High', 'Very High']
    )
    print("Income categories:\n", df['INCOME_CATEGORY'].value_counts())

    # Feature 5 — high risk flag
    df['HIGH_RISK_FLAG'] = (df['CREDIT_TO_INCOME_RATIO'] > 8).astype(int)
    print("High risk applicants:", df['HIGH_RISK_FLAG'].sum())

    # Feature 6 — employment stability
    df['IS_STABLE_EMPLOYMENT'] = (df['YEARS_EMPLOYED'] >= 2).astype(int)
    print("Stably employed:", df['IS_STABLE_EMPLOYMENT'].sum())

    print("Shape after engineering:", df.shape)
    return df



def save_output(df, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    file_size = os.path.getsize(filepath) / (1024 * 1024)
    print("Saved to:", filepath)
    print("File size:", round(file_size, 1), "MB")
    
    
def main():
    print("=" * 50)
    print("AltScore — Data Cleaning Pipeline")
    print("=" * 50)
    
    df = load_data(INPUT_FILE)
    df = drop_high_missing(df)
    df = fix_days_columns(df)
    df = impute_missing(df)
    df = cap_outliers(df)
    df = engineer_base_features(df)
    save_output(df, OUTPUT_FILE)
    
    print("=" * 50)
    print("Pipeline complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()
    