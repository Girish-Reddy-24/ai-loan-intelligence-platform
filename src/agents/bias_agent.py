def detect_bias(user_data, prediction):
    flags = []

    # Example bias checks
    if user_data.get("state") in ["MS", "LA", "AL"]:
        flags.append("Location-based risk detected")

    if user_data.get("annual_income", 0) < 30000 and prediction == "Rejected":
        flags.append("Income bias possible")

    if user_data.get("credit_score", 0) > 750 and prediction == "Rejected":
        flags.append("High credit score but rejected")

    if len(flags) == 0:
        return "No bias detected"

    return flags