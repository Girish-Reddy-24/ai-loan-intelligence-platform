import requests


def generate_explanation(prediction, user_data):

    prompt = f"""
    You are a financial AI assistant.

    Loan decision: {prediction}

    User data:
    {user_data}

    Explain clearly:
    - Why the decision was made
    - Keep it professional and simple
    """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]