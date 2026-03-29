def assess_risk(user_data):
    score = 0

    # Credit score
    if user_data.get("credit_score", 0) < 600:
        score += 2
    elif user_data.get("credit_score", 0) < 700:
        score += 1

    # Existing debt
    if user_data.get("existing_debt_payments_monthly", 0) > 1000:
        score += 2
    elif user_data.get("existing_debt_payments_monthly", 0) > 500:
        score += 1

    # Income vs expenses
    income = user_data.get("monthly_income", 1)
    expenses = user_data.get("monthly_expenses", 0)

    if expenses > income:
        score += 2
    elif expenses > 0.7 * income:
        score += 1

    # Final classification
    if score >= 4:
        return "High Risk"
    elif score >= 2:
        return "Medium Risk"
    else:
        return "Low Risk"