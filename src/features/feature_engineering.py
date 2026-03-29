import pandas as pd
import os
from datetime import datetime

RAW_DATA_PATH = "data/raw/"
PROCESSED_DATA_PATH = "data/processed/"


# =========================
# LOAD DATA
# =========================
def load_latest_raw_data():
    files = os.listdir(RAW_DATA_PATH)
    files = [f for f in files if f.endswith(".csv")]

    latest_file = sorted(files)[-1]
    path = os.path.join(RAW_DATA_PATH, latest_file)

    df = pd.read_csv(path)
    print(f"[INFO] Loaded raw data: {latest_file}")

    return df


# =========================
# CLEAN DATA
# =========================
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [col.strip().lower() for col in df.columns]

    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
    categorical_cols = df.select_dtypes(include=["object", "string"]).columns

    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

    for col in categorical_cols:
        df[col] = df[col].fillna(df[col].mode()[0])

    print("[INFO] Missing value handling completed")
    return df


# =========================
# FEATURE ENGINEERING + SELECTION
# =========================
def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:

    eps = 1e-5

    # Core financial features
    df["monthly_income"] = df["monthly_income"].replace(0, eps)

    df["debt_to_income"] = (
        df["monthly_expenses"] + df["existing_debt_payments_monthly"]
    ) / df["monthly_income"]

    df["loan_to_income"] = df["loan_amount"] / (df["annual_income"] + eps)

    df["loan_to_value"] = df["loan_amount"] / (df["property_value"] + eps)

    df["income_after_expenses"] = df["monthly_income"] - df["monthly_expenses"]

    df["credit_score_normalized"] = df["credit_score"] / 850

    df["high_risk_flag"] = (df["debt_to_income"] > 0.4).astype(int)

    print("[INFO] Advanced feature engineering completed")

    # ======================
    # FEATURE SELECTION (VERY IMPORTANT)
    # ======================
    important_cols = [
        "annual_income",
        "monthly_income",
        "monthly_expenses",
        "loan_amount",
        "existing_debt_payments_monthly",
        "credit_score",
        "num_credit_accounts",
        "property_value",
        "debt_to_income",
        "loan_to_income",
        "loan_to_value",
        "income_after_expenses",
        "credit_score_normalized",
        "high_risk_flag"
    ]

    cols_to_keep = important_cols.copy()

    if "loan_status" in df.columns:
        cols_to_keep.append("loan_status")

    df = df[cols_to_keep]

    print("[INFO] Feature selection applied")

    return df


# =========================
# ENCODING
# =========================
def encode_categorical(df: pd.DataFrame) -> pd.DataFrame:

    if "loan_status" in df.columns:

        df["loan_status"] = df["loan_status"].astype(str).str.strip().str.lower()

        # Keep only valid labels
        df = df[df["loan_status"].isin(["approved", "rejected"])]

        if len(df) == 0:
            raise ValueError("No valid data after filtering loan_status")

        target = df["loan_status"].map({
            "rejected": 0,
            "approved": 1
        })

        df_features = df.drop("loan_status", axis=1)

        df_features["loan_status"] = target

    else:
        df_features = df.copy()

    print("[INFO] Encoding completed")

    return df_features


# =========================
# SAVE
# =========================
def save_processed_data(df: pd.DataFrame):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"loan_processed_{timestamp}.csv"

    path = os.path.join(PROCESSED_DATA_PATH, file_name)
    df.to_csv(path, index=False)

    print(f"[INFO] Processed data saved at {path}")


# =========================
# PIPELINE
# =========================
def run_feature_pipeline():
    df = load_latest_raw_data()
    df = clean_data(df)
    df = feature_engineering(df)
    df = encode_categorical(df)
    save_processed_data(df)


if __name__ == "__main__":
    run_feature_pipeline()
    