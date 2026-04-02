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
# SIMPLE SAFE PREDICT (NO CRASH)
# =========================
@app.post("/predict")
def predict(data: dict, background_tasks: BackgroundTasks):

    try:
        # SAFE INPUT
        income = float(data.get("monthly_income", 0))
        expenses = float(data.get("monthly_expenses", 0))
        loan = float(data.get("loan_amount", 0))
        credit = float(data.get("credit_score", 0))
        debt = float(data.get("existing_debt_payments_monthly", 0))

        if income == 0:
            return {"error": "Invalid income"}

        # =========================
        # CALCULATIONS
        # =========================
        dti = (expenses + debt) / income
        lti = loan / (income * 12)

        # =========================
        # DECISION LOGIC
        # =========================
        if credit < 550 or dti > 0.7 or lti > 2:
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
            "reasons": ["Calculated based on financial ratios"],
            "loan_optimizer": {"max_safe_loan": int(income * 12 * 0.5)},
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