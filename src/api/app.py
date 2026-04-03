from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.llm.explainer import generate_explanation
import os
import uuid
import joblib

# ✅ KEEP THIS IMPORT (DO NOT CHANGE)
from src.engine.simulation_engine import simulate_loan

app = FastAPI()

# =========================
# SERVE UI
# =========================
if os.path.exists("src/static"):
    app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.get("/")
def serve_ui():
    if os.path.exists("src/static/index.html"):
        return FileResponse("src/static/index.html")
    return {"message": "Loan AI System Running"}

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

# =========================
# LOAD MODEL (SAFE)
# =========================
MODEL_PATH = "models/loan_model.pkl"
model = None

if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
        print("✅ ML Model Loaded")
    except Exception as e:
        print("❌ Model load failed:", e)

# =========================
# HELPER
# =========================
def safe_float(val):
    try:
        return float(val)
    except:
        return 0.0

# =========================
# AI EXPLANATION
# =========================
def generate_explanation(prediction, dti, lti, credit):
    text = f"Loan Decision: {prediction}\n\n"

    text += "Financial Summary:\n"
    text += f"- Debt-to-Income (DTI): {round(dti,2)}\n"
    text += f"- Loan-to-Income (LTI): {round(lti,2)}\n"
    text += f"- Credit Score: {credit}\n\n"

    text += "Explanation:\n"

    if prediction == "Approved":
        text += "The loan was approved because your financial profile is stable.\n"

        if dti < 0.5:
            text += "- Your debt-to-income ratio is manageable.\n"

        if credit >= 700:
            text += "- Strong credit history supports approval.\n"

        if lti < 0.5:
            text += "- Loan amount is reasonable relative to income.\n"

    else:
        text += "The loan was rejected due to higher financial risk.\n"

        if dti > 0.6:
            text += "- A large portion of your income is already committed.\n"

        if lti > 1:
            text += "- Loan amount is too high compared to income.\n"

        if credit < 650:
            text += "- Credit score indicates higher risk.\n"

    return text

# =========================
# PREDICT
# =========================
@app.post("/predict")
def predict(data: dict):

    try:
        # =========================
        # INPUT HANDLING
        # =========================
        annual_income = safe_float(data.get("annual_income"))
        monthly_income_input = safe_float(data.get("monthly_income"))

        income = annual_income / 12 if annual_income > 0 else monthly_income_input

        expenses = safe_float(data.get("monthly_expenses"))
        loan = safe_float(data.get("loan_amount"))
        credit = safe_float(data.get("credit_score"))
        debt = safe_float(data.get("existing_debt_payments_monthly"))

        # =========================
        # VALIDATION
        # =========================
        if income <= 0:
            return {"error": "Income must be greater than 0"}

        if loan <= 0:
            return {"error": "Loan must be greater than 0"}

        if not (300 <= credit <= 900):
            return {"error": "Credit score must be between 300-900"}

        # =========================
        # CALCULATIONS
        # =========================
        dti = (expenses + debt) / income
        lti = loan / (income * 12)

        # =========================
        # SAFE LOAN
        # =========================
        disposable_income = income - expenses - debt

        if disposable_income <= 0:
            max_safe_loan = income * 2
        else:
            max_safe_loan = disposable_income * 12 * 0.6

        # =========================
        # ML PREDICTION (SAFE)
        # =========================
        ml_prediction = None

        if model:
            try:
                features = [[income, expenses, loan, credit, debt]]
                ml_prediction = model.predict(features)[0]
            except Exception as e:
                print("ML error:", e)

        # =========================
        # FINAL DECISION
        # =========================
        if ml_prediction is not None:
            result = "Approved" if ml_prediction == 1 else "Rejected"
        else:
            if credit < 550 or dti > 0.7 or lti > 2:
                result = "Rejected"
            elif loan > max_safe_loan:
                result = "Rejected"
            elif credit >= 700 and dti < 0.6:
                result = "Approved"
            else:
                result = "Rejected"

        # =========================
        # RISK
        # =========================
        if dti > 0.7 or lti > 2:
            risk = "High Risk"
        elif dti < 0.4:
            risk = "Low Risk"
        else:
            risk = "Medium Risk"

        # =========================
        # EXPLANATION
        # =========================
        explanation = generate_explanation(result, dti, lti, credit)

        request_id = str(uuid.uuid4())

        # =========================
        # RESPONSE
        # =========================
        return {
            "request_id": request_id,
            "prediction": result,
            "risk_level": risk,
            "confidence_score": 0.9,
            "reasons": [
                f"DTI: {round(dti,2)}",
                f"LTI: {round(lti,2)}"
            ],
            "loan_optimizer": {
                "max_safe_loan": int(max_safe_loan)
            },
            "explanation": generate_explanation(result, dti, lti, credit)
        }

    except Exception as e:
        print("ERROR:", e)
        return {"error": "Backend failure"}

# =========================
# SIMULATION
# =========================
@app.post("/simulate")
def simulate(data: dict):
    return {"simulation": simulate_loan(data)}
