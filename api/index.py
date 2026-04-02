from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "AI Loan API Running on Vercel"}

@app.post("/predict")
def predict(data: dict):

    income = data["monthly_income"]
    expenses = data["monthly_expenses"]
    loan = data["loan_amount"]
    credit = data["credit_score"]

    dti = expenses / income
    lti = loan / (income * 12)

    # SIMPLE RULE ENGINE (Vercel-safe)
    if credit < 600 or dti > 0.6 or lti > 2:
        result = "Rejected"
    else:
        result = "Approved"

    return {
        "prediction": result,
        "dti": round(dti, 2),
        "lti": round(lti, 2),
        "message": "Processed on Vercel"
    }