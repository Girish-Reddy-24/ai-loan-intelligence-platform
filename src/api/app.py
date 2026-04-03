from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

import os
import pandas as pd
import uuid
import json

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
# HELPER (SAFE FLOAT)
# =========================
def safe_float(val):
    try:
        return float(val)
    except:
        return 0.0

# =========================
# PREDICT (PRODUCTION SAFE)
# =========================
@app.post("/predict")
def predict(data: dict, background_tasks: BackgroundTasks):

    try:
        # =========================
        # INPUT HANDLING
        # =========================
        annual_income = safe_float(data.get("annual_income"))
        monthly_income_input = safe_float(data.get("monthly_income"))

        # ✅ AUTO FIX (no inconsistency)
        if annual_income > 0:
            income = annual_income / 12
        else:
            income = monthly_income_input

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

        if credit < 300 or credit > 900:
            return {"error": "Credit score must be between 300-900"}

        # =========================
        # CALCULATIONS
        # =========================
        dti = (expenses + debt) / income
        lti = loan / (income * 12)

        # =========================
        # DECISION LOGIC (FIXED)
        # =========================
        max_safe_loan = income * 12 * 0.5

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
            "explanation": "Click Get Explanation"
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

# =========================
# EXPLANATION (SAFE)
# =========================
@app.get("/explanation/{request_id}")
def get_explanation(request_id: str):
    return {"explanation": "Explanation will be added soon"}
