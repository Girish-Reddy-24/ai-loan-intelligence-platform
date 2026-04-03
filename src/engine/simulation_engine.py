def simulate_loan(data):
    income = data["monthly_income"]
    expenses = data["monthly_expenses"]
    debt = data.get("existing_debt_payments_monthly", 0)
    loan = data["loan_amount"]
    credit = data["credit_score"]

    # =========================
    # CALCULATIONS
    # =========================
    dti = (expenses + debt) / income if income > 0 else 1.0
    annual_income = income * 12
    lti = loan / annual_income if annual_income > 0 else 1.0

    # =========================
    # APPROVAL PROBABILITY
    # =========================
    # Align probability with decision strength
    prob = 0.85 if credit >= 700 and dti < 0.5 else 0.6

    # DTI impact
    if dti > 0.6:
        prob -= 0.4
    elif dti > 0.5:
        prob -= 0.2

    if credit < 650:
        prob -= 0.3
    elif credit >= 750:
        prob += 0.1

    if lti > 1:
        prob -= 0.3
    elif lti < 0.5:
        prob += 0.05

    # Credit impact
    if credit < 600:
        prob -= 0.3
    elif credit < 700:
        prob -= 0.1
    elif credit > 750:
        prob += 0.1

    # LTI impact
    if lti > 2:
        prob -= 0.3
    elif lti > 1:
        prob -= 0.1
    else:
        prob += 0.1

    prob = max(0.05, min(prob, 0.95))

    # =========================
    # SAFE LOAN CALCULATION (FIXED)
    # =========================
    disposable_income = income - expenses - debt

    if disposable_income <= 0:
        max_safe_loan = int(income * 3)   # 🔥 NEVER ZERO
    else:
        max_safe_loan = int(disposable_income * 12 * 0.5)

    max_safe_loan = max(max_safe_loan, 1000)

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

    if not recommendations:
        recommendations.append("You are financially healthy for this loan")

    return {
        "max_safe_loan": max_safe_loan,
        "approval_probability": round(prob, 2),
        "recommendations": recommendations
    }