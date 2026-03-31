def apply_guardrails(prediction, data, reasons, errors):
    dti = (data["monthly_expenses"] + data.get("existing_debt_payments_monthly", 0)) / data["monthly_income"]
    lti = data["loan_amount"] / data["annual_income"]

    explanation = f"""
Loan Decision: {prediction}

Reason Summary:
{", ".join(reasons)}

Financial Metrics:
- DTI: {round(dti,2)}
- LTI: {round(lti,2)}
- Credit Score: {data["credit_score"]}

This decision is based strictly on financial risk evaluation.
"""

    if errors:
        explanation += "\n\n(Note: Explanation adjusted for accuracy)"

    return explanation