from src.engine.loan_optimizer import optimize_loan_amount
from src.engine.simulation_engine import simulate_loan

from fastapi import FastAPI, BackgroundTasks
import joblib
import os
import pandas as pd
import uuid
import json
from fastapi.middleware.cors import CORSMiddleware

from src.features.feature_engineering import clean_data, feature_engineering, encode_categorical
from src.agents.offer_agent import generate_offer
from src.agents.bias_agent import detect_bias
from src.utils.logger import log_prediction
from src.agents.risk_engine import calculate_risk, get_risk_tier, recommend_loan

try:
    from src.explainability.shap_explainer import get_shap_explanation
except:
    def get_shap_explanation(model, df):
        return []


app = FastAPI()

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "models/"


# =========================
# LOAD MODEL
# =========================
def load_latest_model():
    try:
        files = [f for f in os.listdir(MODEL_PATH) if f.endswith(".pkl")]

        if not files:
            print("⚠️ No model found")
            return None

        latest_model = sorted(files)[-1]
        path = os.path.join(MODEL_PATH, latest_model)

        model = joblib.load(path)
        print(f"[INFO] Loaded model: {latest_model}")
        return model

    except Exception as e:
        print("❌ Model loading failed:", e)
        return None


model = load_latest_model()


# =========================
# HOME
# =========================
@app.get("/")
def home():
    return {"message": "Loan AI System Running"}


# =========================
# REASONS
# =========================
def generate_reasons(data, result):
    reasons = []

    dti = (data["monthly_expenses"] + data["existing_debt_payments_monthly"]) / data["monthly_income"]
    lti = data["loan_amount"] / data["annual_income"]

    if dti > 0.6:
        reasons.append("High debt-to-income ratio")
    elif dti > 0.4:
        reasons.append("Moderate debt-to-income ratio")

    if lti > 1:
        reasons.append("Loan amount too high compared to income")

    if data["credit_score"] < 650:
        reasons.append("Low credit score")

    if data["credit_score"] > 750:
        reasons.append("Excellent credit score")

    if result == "Approved" and not reasons:
        reasons.append("Strong financial profile")

    return reasons


# =========================
# EXPLANATION (ASYNC)
# =========================
def generate_explanation_async(request_id, result, data, shap_values):
    from src.llm.explainer import generate_explanation

    explanation = generate_explanation(result, data, shap_values)

    file_path = "data/explanations.json"

    try:
        with open(file_path, "r") as f:
            records = json.load(f)
    except:
        records = []

    records.append({
        "id": request_id,
        "explanation": explanation
    })

    with open(file_path, "w") as f:
        json.dump(records, f, indent=2)


# =========================
# INTERNAL LOGIC (USED BY OPTIMIZER)
# =========================
def internal_predict_logic(data):
    dti = (data["monthly_expenses"] + data["existing_debt_payments_monthly"]) / data["monthly_income"]
    lti = data["loan_amount"] / data["annual_income"]

    if data["credit_score"] < 550:
        return "Rejected"

    elif dti > 0.6:
        return "Rejected"

    elif lti > 2:
        return "Rejected"

    elif data["credit_score"] >= 720 and dti < 0.4:
        return "Approved"

    elif data["credit_score"] >= 680 and dti < 0.5:
        return "Approved"

    else:
        return "Rejected"


# =========================
# PREDICT API
# =========================
@app.post("/predict")
def predict(data: dict, background_tasks: BackgroundTasks):

    # DEFAULTS
    data.setdefault("num_credit_accounts", 5)
    data.setdefault("property_value", 300000)
    data.setdefault("existing_debt_payments_monthly", 0)

    request_id = str(uuid.uuid4())

    # -------------------------
    # DATA PROCESSING
    # -------------------------
    df = pd.DataFrame([data])

    df = clean_data(df)
    df = feature_engineering(df)
    df = encode_categorical(df)

    model_features = model.get_booster().feature_names

    missing_cols = list(set(model_features) - set(df.columns))
    if missing_cols:
        df_missing = pd.DataFrame(0, index=df.index, columns=missing_cols)
        df = pd.concat([df, df_missing], axis=1)

    df = df[model_features]

    # -------------------------
    # MODEL
    # -------------------------
    if model:
        prediction = model.predict(df)[0]
        confidence = float(max(model.predict_proba(df)[0]))
    else:
        prediction = 1 if data["credit_score"] > 650 else 0
        confidence = 0.5

    # -------------------------
    # DECISION ENGINE (FINAL)
    # -------------------------
    dti = (data["monthly_expenses"] + data["existing_debt_payments_monthly"]) / data["monthly_income"]
    lti = data["loan_amount"] / data["annual_income"]

    if data["credit_score"] < 550:
        result = "Rejected"

    elif dti > 0.7:
        result = "Rejected"

    elif lti > 2:
        result = "Rejected"

    elif data["credit_score"] >= 700 and dti < 0.6 and lti < 1:
        result = "Approved"

    elif data["credit_score"] >= 650 and dti < 0.6:
        result = "Approved"

    else:
        result = "Rejected"

    # -------------------------
    # RISK (ALIGNED)
    # -------------------------
    if dti > 0.7 or lti > 2:
        risk_level = "High Risk"
    elif dti < 0.4 and data["credit_score"] > 720:
        risk_level = "Low Risk"
    else:
        risk_level = "Medium Risk"

    # 🔥 FINAL GUARDRAIL
    if risk_level == "High Risk":
        result = "Rejected"

    # -------------------------
    # OTHER COMPONENTS
    # -------------------------
    reasons = generate_reasons(data, result)

    offer = generate_offer(result, data)
    bias_flags = detect_bias(data, result)

    risk_score = calculate_risk(data)
    risk_tier = get_risk_tier(risk_score)
    recommended_loan = recommend_loan(data)

    try:
        shap_explanation = get_shap_explanation(model, df)
    except:
        shap_explanation = []

    optimizer_result = optimize_loan_amount(data, internal_predict_logic)

    # -------------------------
    # RESPONSE
    # -------------------------
    response = {
        "request_id": request_id,
        "prediction": result,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "risk_tier": risk_tier,
        "recommended_loan": recommended_loan,
        "offer": offer,
        "bias_detection": bias_flags,
        "confidence_score": round(confidence, 2),
        "reasons": reasons,
        "shap_explanation": shap_explanation,
        "loan_optimizer": optimizer_result,
        "explanation": "Click 'Get Explanation'"
    }

    log_prediction(data, response)

    background_tasks.add_task(
        generate_explanation_async,
        request_id,
        result,
        data,
        shap_explanation
    )

    return response


# =========================
# SIMULATION API
# =========================
@app.post("/simulate")
def simulate(data: dict):
    simulation_result = simulate_loan(data)

    return {
        "message": "Simulation successful",
        "simulation": simulation_result
    }


# =========================
# GET EXPLANATION
# =========================
@app.get("/explanation/{request_id}")
def get_explanation(request_id: str):

    file_path = "data/explanations.json"

    try:
        with open(file_path, "r") as f:
            records = json.load(f)
    except:
        return {"message": "No explanations found"}

    for r in records:
        if r["id"] == request_id:
            return {"explanation": r["explanation"]}

    return {"message": "Explanation not ready yet"}