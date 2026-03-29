def simulate_loan(data):
    income = data["monthly_income"]
    expenses = data["monthly_expenses"]
    debt = data["existing_debt_payments_monthly"]
    loan = data["loan_amount"]
    credit = data["credit_score"]

    # =========================
    # CALCULATIONS
    # =========================
    dti = (expenses + debt) / income
    lti = loan / (income * 12)

    # =========================
    # APPROVAL PROBABILITY
    # =========================
    prob = 1.0

    if dti > 0.5:
        prob -= 0.4
    elif dti > 0.4:
        prob -= 0.2

    if credit < 600:
        prob -= 0.4
    elif credit < 700:
        prob -= 0.2
    elif credit > 750:
        prob += 0.1

    if lti > 1:
        prob -= 0.3
    elif lti < 0.5:
        prob += 0.1

    prob = max(0.05, min(prob, 0.95))

    # =========================
    # SAFE LOAN CALCULATION
    # =========================
    max_safe_loan = int((income * 12) * 0.5)

    # =========================
    # RECOMMENDATIONS
    # =========================
    recommendations = []

    if dti > 0.4:
        recommendations.append("Reduce monthly expenses")

    if credit < 700:
        recommendations.append("Improve credit score above 700")

    if loan > max_safe_loan:
        recommendations.append(f"Reduce loan amount below ${max_safe_loan}")

    if len(recommendations) == 0:
        recommendations.append("You are financially healthy for this loan")

    return {
        "max_safe_loan": max_safe_loan,
        "approval_probability": round(prob, 2),
        "recommendations": recommendations
    }