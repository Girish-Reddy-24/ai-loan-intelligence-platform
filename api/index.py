from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Vercel FastAPI working"}

@app.post("/predict")
def predict(data: dict):
    return {"prediction": "Approved"}