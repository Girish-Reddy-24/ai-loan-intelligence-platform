def optimize_loan_amount(data, predict_function):
    """
    Finds max loan user can get approved
    """

    base_income = data["annual_income"]

    # try loans from small → big
    step = 5000
    max_limit = base_income * 2

    best_loan = 0

    for loan in range(5000, int(max_limit), step):
        test_data = data.copy()
        test_data["loan_amount"] = loan

        result = predict_function(test_data)

        if result == "Approved":
            best_loan = loan
        else:
            break

    return {
        "max_approved_loan": best_loan,
        "message": f"You can safely take up to ${best_loan}"
    }