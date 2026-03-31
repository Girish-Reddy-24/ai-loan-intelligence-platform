def validate_explanation(text, data):
    errors = []

    dti = (data["monthly_expenses"] + data.get("existing_debt_payments_monthly", 0)) / data["monthly_income"]
    lti = data["loan_amount"] / data["annual_income"]

    text_lower = text.lower()

    # -------------------------
    # DTI VALIDATION
    # -------------------------
    if dti < 1 and "expenses exceed income" in text_lower:
        errors.append("DTI mismatch: expenses do NOT exceed income")

    if dti > 1 and "healthy" in text_lower:
        errors.append("DTI mismatch: should NOT be healthy")

    # -------------------------
    # LTI VALIDATION
    # -------------------------
    if lti < 1 and "high risk" in text_lower:
        errors.append("LTI mismatch: should NOT be high risk")

    if lti > 2 and "acceptable" in text_lower:
        errors.append("LTI mismatch: should NOT be acceptable")

    # -------------------------
    # CREDIT SCORE VALIDATION
    # -------------------------
    if data["credit_score"] < 600 and "good credit" in text_lower:
        errors.append("Credit score mismatch")

    return errors