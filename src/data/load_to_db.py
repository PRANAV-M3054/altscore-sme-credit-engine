import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os


# Load the .env file
load_dotenv()

# Read database credentials from .env
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Create connection string
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print("Connecting to:", DB_NAME, "on", DB_HOST)

def create_db_engine():
    engine = create_engine(DB_URL)
    try:
        with engine.connect() as conn:
            print("Database connection successful!")
    except Exception as e:
        print("Connection failed:", e)
    return engine

engine = create_db_engine()

def load_csv_files():
    print("\nLoading CSV files...")
    
    app_df = pd.read_csv("data/processed/application_cleaned.csv")
    print("Application data:", app_df.shape)
    
    gst_df = pd.read_csv("data/simulated/gst_data.csv")
    print("GST data:", gst_df.shape)
    
    return app_df, gst_df

app_df, gst_df = load_csv_files()

def load_dim_business(app_df, engine):
    print("\nLoading dim_business...")
    
    cols = [
        'SK_ID_CURR', 'NAME_CONTRACT_TYPE', 'CODE_GENDER',
        'FLAG_OWN_CAR', 'FLAG_OWN_REALTY', 'NAME_INCOME_TYPE',
        'NAME_EDUCATION_TYPE', 'NAME_FAMILY_STATUS',
        'OCCUPATION_TYPE', 'ORGANIZATION_TYPE',
        'IS_SME', 'INCOME_CATEGORY'
    ]
    
    dim_business = app_df[cols].copy()
    dim_business['INCOME_CATEGORY'] = dim_business['INCOME_CATEGORY'].astype(str)
    
    dim_business.to_sql(
        name      = 'dim_business',
        con       = engine,
        if_exists = 'replace',
        index     = False,
        chunksize = 10000
    )
    print("Rows loaded:", len(dim_business))
    
    
    
def reset_tables(engine):
    print("\nResetting tables...")
    with engine.connect() as conn:
        conn.execute(__import__('sqlalchemy').text("""
            DROP TABLE IF EXISTS ml_predictions CASCADE;
            DROP TABLE IF EXISTS fact_loan_applications CASCADE;
            DROP TABLE IF EXISTS dim_gst CASCADE;
            DROP TABLE IF EXISTS dim_cashflow CASCADE;
            DROP TABLE IF EXISTS dim_business CASCADE;
        """))
        conn.commit()
    print("All tables dropped successfully")
    
    
engine = create_db_engine()
app_df, gst_df = load_csv_files()
reset_tables(engine)
load_dim_business(app_df, engine)



def load_dim_cashflow(app_df, engine):
    print("\nLoading dim_cashflow...")
    
    cols = [
        'SK_ID_CURR', 'AMT_INCOME_TOTAL', 'AMT_CREDIT',
        'AMT_ANNUITY', 'AMT_GOODS_PRICE', 'CREDIT_TO_INCOME_RATIO',
        'ANNUITY_TO_INCOME_RATIO', 'HIGH_RISK_FLAG',
        'IS_STABLE_EMPLOYMENT'
    ]
    
    dim_cashflow = app_df[cols].copy()
    dim_cashflow.to_sql(
        name      = 'dim_cashflow',
        con       = engine,
        if_exists = 'replace',
        index     = False,
        chunksize = 10000
    )
    print("Rows loaded:", len(dim_cashflow))


def load_dim_gst(gst_df, engine):
    print("\nLoading dim_gst...")
    
    gst_df.to_sql(
        name      = 'dim_gst',
        con       = engine,
        if_exists = 'replace',
        index     = False,
        chunksize = 10000
    )
    print("Rows loaded:", len(gst_df))


def load_fact_table(app_df, engine):
    print("\nLoading fact_loan_applications...")
    
    cols = [
        'SK_ID_CURR', 'TARGET', 'AGE_YEARS', 'YEARS_EMPLOYED',
        'REGION_RATING_CLIENT', 'EXT_SOURCE_1', 'EXT_SOURCE_2',
        'EXT_SOURCE_3'
    ]
    
    fact_df = app_df[cols].copy()
    fact_df.to_sql(
        name      = 'fact_loan_applications',
        con       = engine,
        if_exists = 'replace',
        index     = False,
        chunksize = 10000
    )
    print("Rows loaded:", len(fact_df))
    
    
    
    
def main():
    print("=" * 50)
    print("AltScore — Database Loading Pipeline")
    print("=" * 50)

    engine = create_db_engine()
    app_df, gst_df = load_csv_files()
    reset_tables(engine)
    load_dim_business(app_df, engine)
    load_dim_cashflow(app_df, engine)
    load_dim_gst(gst_df, engine)
    load_fact_table(app_df, engine)

    print("\n" + "=" * 50)
    print("All tables loaded successfully!")
    print("=" * 50)

if __name__ == "__main__":
    main()