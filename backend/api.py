from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 1) Khoi tao app
app = FastAPI(title="Tiki Sentiment Analysis API")

# 2) Load model bang duong dan theo vi tri file nay
MODEL_PATH = Path(__file__).with_name("model.pkl")

try:
    model_pipeline = joblib.load(MODEL_PATH)
    print(f"Da tai model thanh cong: {MODEL_PATH}")
except FileNotFoundError:
    model_pipeline = None
    print(f"Loi: Khong tim thay file model tai {MODEL_PATH}")


# 3) Dinh nghia input
class ReviewRequest(BaseModel):
    comment: str


@app.get("/")
def root():
    return {"message": "API is running"}


@app.post("/predict")
def predict_sentiment(request: ReviewRequest):
    if model_pipeline is None:
        raise HTTPException(
            status_code=500,
            detail=f"Model chua duoc load. Kiem tra file: {MODEL_PATH}",
        )

    user_comment = request.comment
    prediction = model_pipeline.predict([user_comment])
    result = prediction[0]

    if result == 1:
        return {"sentiment": "Tich_Cuc", "status_code": 200}
    return {"sentiment": "Tieu_Cuc", "status_code": 200}