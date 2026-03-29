def generate_offer(prediction, user_data):
    if prediction == "Approved":
        return "Full loan approved"

    # If rejected → suggest smaller loan
    income = user_data.get("monthly_income", 0)
    expenses = user_data.get("monthly_expenses", 0)

    disposable_income = income - expenses

    if disposable_income <= 0:
        return "No loan offer available"

    # simple rule: 30% of annual income
    suggested_loan = int(user_data.get("annual_income", 0) * 0.3)

    return f"You may qualify for a smaller loan of ${suggested_loan}"

