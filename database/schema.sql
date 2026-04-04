-- AltScore SME Credit Intelligence Engine
-- Database Schema — PostgreSQL 18
-- Run this file to recreate the full star schema
-- Usage: psql -U postgres -d altscore_db -f database/schema.sql

-- ─────────────────────────────────────────
-- Drop existing tables (safe reset)
-- ─────────────────────────────────────────
DROP TABLE IF EXISTS ml_predictions CASCADE;
DROP TABLE IF EXISTS fact_loan_applications CASCADE;
DROP TABLE IF EXISTS dim_gst CASCADE;
DROP TABLE IF EXISTS dim_cashflow CASCADE;
DROP TABLE IF EXISTS dim_business CASCADE;

-- ─────────────────────────────────────────
-- Dimension Tables
-- ─────────────────────────────────────────

CREATE TABLE dim_business (
    SK_ID_CURR          INTEGER PRIMARY KEY,
    NAME_CONTRACT_TYPE  VARCHAR(50),
    CODE_GENDER         VARCHAR(5),
    FLAG_OWN_CAR        VARCHAR(5),
    FLAG_OWN_REALTY     VARCHAR(5),
    NAME_INCOME_TYPE    VARCHAR(100),
    NAME_EDUCATION_TYPE VARCHAR(100),
    NAME_FAMILY_STATUS  VARCHAR(100),
    OCCUPATION_TYPE     VARCHAR(100),
    ORGANIZATION_TYPE   VARCHAR(100),
    IS_SME              INTEGER,
    INCOME_CATEGORY     VARCHAR(20)
);

CREATE TABLE dim_cashflow (
    SK_ID_CURR              INTEGER PRIMARY KEY,
    AMT_INCOME_TOTAL        FLOAT,
    AMT_CREDIT              FLOAT,
    AMT_ANNUITY             FLOAT,
    AMT_GOODS_PRICE         FLOAT,
    CREDIT_TO_INCOME_RATIO  FLOAT,
    ANNUITY_TO_INCOME_RATIO FLOAT,
    HIGH_RISK_FLAG          INTEGER,
    IS_STABLE_EMPLOYMENT    INTEGER
);

CREATE TABLE dim_gst (
    SK_ID_CURR              INTEGER PRIMARY KEY,
    GST_REGISTERED          INTEGER,
    GST_FILING_COMPLIANCE   FLOAT,
    GST_QUARTERLY_TURNOVER  FLOAT,
    GST_TURNOVER_GROWTH     FLOAT,
    GST_FILING_STREAK       INTEGER,
    CASH_FLOW_RATIO         FLOAT,
    GST_PENALTY_COUNT       INTEGER
);

-- ─────────────────────────────────────────
-- Fact Table
-- ─────────────────────────────────────────

CREATE TABLE fact_loan_applications (
    SK_ID_CURR           INTEGER PRIMARY KEY,
    TARGET               INTEGER,
    AGE_YEARS            FLOAT,
    YEARS_EMPLOYED       FLOAT,
    REGION_RATING_CLIENT INTEGER,
    EXT_SOURCE_1         FLOAT,
    EXT_SOURCE_2         FLOAT,
    EXT_SOURCE_3         FLOAT,
    ML_RISK_SCORE        FLOAT DEFAULT NULL,
    ML_RISK_TIER         VARCHAR(20) DEFAULT NULL,
    CREATED_AT           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
-- ML Predictions Table
-- ─────────────────────────────────────────

CREATE TABLE ml_predictions (
    PREDICTION_ID       SERIAL PRIMARY KEY,
    SK_ID_CURR          INTEGER,
    ML_RISK_SCORE       FLOAT,
    ML_RISK_TIER        VARCHAR(20),
    SHAP_TOP_FEATURE_1  VARCHAR(100),
    SHAP_TOP_FEATURE_2  VARCHAR(100),
    SHAP_TOP_FEATURE_3  VARCHAR(100),
    LLM_REJECTION_LETTER TEXT,
    PREDICTED_AT        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
-- Useful Views
-- ─────────────────────────────────────────

CREATE OR REPLACE VIEW vw_sme_risk_summary AS
SELECT 
    b."IS_SME",
    b."NAME_INCOME_TYPE",
    b."INCOME_CATEGORY",
    COUNT(*) AS total_applicants,
    SUM(f."TARGET") AS total_defaulters,
    ROUND(AVG(f."TARGET")::numeric * 100, 2) AS default_rate_pct,
    ROUND(AVG(c."CREDIT_TO_INCOME_RATIO")::numeric, 2) AS avg_credit_ratio,
    ROUND(AVG(g."GST_FILING_COMPLIANCE")::numeric, 3) AS avg_gst_compliance,
    ROUND(AVG(g."CASH_FLOW_RATIO")::numeric, 3) AS avg_cashflow
FROM fact_loan_applications f
JOIN dim_business b ON f."SK_ID_CURR" = b."SK_ID_CURR"
JOIN dim_cashflow c ON f."SK_ID_CURR" = c."SK_ID_CURR"
JOIN dim_gst g ON f."SK_ID_CURR" = g."SK_ID_CURR"
GROUP BY b."IS_SME", b."NAME_INCOME_TYPE", b."INCOME_CATEGORY"
ORDER BY default_rate_pct DESC;

CREATE OR REPLACE VIEW vw_high_risk_applicants AS
SELECT
    f."SK_ID_CURR",
    f."TARGET",
    f."EXT_SOURCE_2",
    c."CREDIT_TO_INCOME_RATIO",
    c."HIGH_RISK_FLAG",
    g."GST_FILING_COMPLIANCE",
    g."CASH_FLOW_RATIO",
    g."GST_PENALTY_COUNT"
FROM fact_loan_applications f
JOIN dim_cashflow c ON f."SK_ID_CURR" = c."SK_ID_CURR"
JOIN dim_gst g ON f."SK_ID_CURR" = g."SK_ID_CURR"
WHERE c."HIGH_RISK_FLAG" = 1
ORDER BY c."CREDIT_TO_INCOME_RATIO" DESC;