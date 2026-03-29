import logging
import os

# Ensure logs folder exists
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def log_prediction(data, result):
    try:
        logging.info(f"Input: {data} | Prediction: {result}")
    except Exception as e:
        print("Logging error:", e)