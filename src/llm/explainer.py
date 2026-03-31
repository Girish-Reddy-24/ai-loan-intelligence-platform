def generate_explanation(prediction, user_data, shap_values=None):

    # =========================
    # SAFE CALCULATIONS
    # =========================
    monthly_income = user_data["monthly_income"]
    monthly_expenses = user_data["monthly_expenses"]
    debt = user_data.get("existing_debt_payments_monthly", 0)

    annual_income = user_data["annual_income"]
    loan_amount = user_data["loan_amount"]
    credit_score = user_data["credit_score"]

    dti = (monthly_expenses + debt) / monthly_income if monthly_income > 0 else 1
    lti = loan_amount / annual_income if annual_income > 0 else 1

    # =========================
    # CLASSIFICATION
    # =========================
    if dti < 0.4:
        dti_status = "healthy"
        dti_text = "Your expenses are well within your income, indicating strong financial stability."
    elif dti < 0.6:
        dti_status = "moderate risk"
        dti_text = "A moderate portion of your income is committed to expenses."
    else:
        dti_status = "high risk"
        dti_text = "A large portion of your income is already committed to expenses, increasing financial risk."

    if lti < 1:
        lti_status = "acceptable"
        lti_text = "The loan amount is reasonable compared to your annual income."
    elif lti < 2:
        lti_status = "elevated risk"
        lti_text = "The loan amount is relatively high compared to your income."
    else:
        lti_status = "very high risk"
        lti_text = "The loan amount is significantly higher than your income, increasing repayment risk."

    if credit_score < 600:
        credit_status = "high risk"
        credit_text = "Your credit profile indicates higher risk."
    elif credit_score < 700:
        credit_status = "moderate"
        credit_text = "Your credit profile is moderate."
    else:
        credit_status = "strong"
        credit_text = "Your credit profile is strong and supports repayment ability."

    # =========================
    # DECISION LOGIC TEXT
    # =========================
    if prediction == "Approved":
        decision_text = (
            "The loan was approved because your overall financial profile is stable and within acceptable risk limits."
        )
    else:
        decision_text = (
            "The loan was rejected because your financial profile indicates a higher risk of repayment difficulty."
        )

    # =========================
    # FINAL EXPLANATION
    # =========================
    return f"""
Loan Decision: {prediction}

Financial Summary:
- Debt-to-Income (DTI): {round(dti,2)} ({dti_status})
- Loan-to-Income (LTI): {round(lti,2)} ({lti_status})
- Credit Score: {credit_score} ({credit_status})

Explanation:

{decision_text}

{dti_text}

{lti_text}

{credit_text}

The decision is based on your ability to manage additional financial obligations while maintaining a stable financial position.
"""