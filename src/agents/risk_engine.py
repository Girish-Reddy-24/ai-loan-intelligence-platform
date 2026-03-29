def calculate_risk(data):
    income = data["annual_income"]
    monthly_income = data["monthly_income"]
    expenses = data["monthly_expenses"]
    debt = data["existing_debt_payments_monthly"]
    loan = data["loan_amount"]
    credit = data["credit_score"]

    dti = (expenses + debt) / monthly_income
    lti = loan / income

    score = 100

    # Penalize high debt
    if dti > 0.5:
        score -= 40
    elif dti > 0.4:
        score -= 25
    elif dti > 0.3:
        score -= 10

    # Penalize large loan
    if lti > 2:
        score -= 30
    elif lti > 1:
        score -= 15

    # Credit score impact
    if credit < 600:
        score -= 30
    elif credit < 700:
        score -= 15

    return max(score, 0)


def get_risk_tier(score):
    if score >= 80:
        return "Gold"
    elif score >= 60:
        return "Silver"
    else:
        return "Risky"


def recommend_loan(data):
    safe_loan = data["annual_income"] * 0.6
    return f"You can safely take up to ${int(safe_loan)}"