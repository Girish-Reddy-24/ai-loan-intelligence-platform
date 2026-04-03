def generate_explanation(prediction, dti, lti, credit):

    text = f"Loan Decision: {prediction}\n\n"

    text += "Financial Summary:\n"
    text += f"- DTI: {round(dti,2)}\n"
    text += f"- LTI: {round(lti,2)}\n"
    text += f"- Credit Score: {credit}\n\n"

    text += "Explanation:\n"

    if prediction == "Approved":
        text += "Your loan is approved because:\n"

        if dti < 0.5:
            text += "- Your expenses are under control.\n"

        if credit >= 700:
            text += "- You have a strong credit score.\n"

        if lti < 0.5:
            text += "- Loan amount is reasonable.\n"

    else:
        text += "Your loan is rejected because:\n"

        if dti > 0.6:
            text += "- Your expenses are too high.\n"

        if lti > 1:
            text += "- Loan amount is too high.\n"

        if credit < 650:
            text += "- Credit score is low.\n"

    return text