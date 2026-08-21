from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import joblib
import os

app = FastAPI()

# Đọc tên bucket từ biến môi trường
BUCKET_NAME = (
    os.environ.get("AWS_BUCKET")
    or os.environ.get("CLOUD_BUCKET")
    or os.environ.get("GCS_BUCKET", "")
)
MODEL_KEY = "models/latest/model.pkl"
MODEL_PATH = os.path.expanduser("~/models/model.pkl")


def download_model():
    """
    Tai file model.pkl tu AWS S3 ve may khi server khoi dong.

    Ham nay duoc goi mot lan khi module duoc import.
    """
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    s3_client = boto3.client("s3")
    print(f"Dang tai model tu s3://{BUCKET_NAME}/{MODEL_KEY} ve {MODEL_PATH}...")
    s3_client.download_file(BUCKET_NAME, MODEL_KEY, MODEL_PATH)
    print("Model da duoc tai xuong tu S3 thanh cong.")


if os.environ.get("SKIP_MODEL_DOWNLOAD") != "1":
    download_model()
    model = joblib.load(MODEL_PATH)
else:
    model = None


class PredictRequest(BaseModel):
    features: list[float]


@app.get("/health")
def health():
    """
    Endpoint kiem tra suc khoe server.
    GitHub Actions goi endpoint nay sau khi deploy de xac nhan server dang chay.

    Tra ve: {"status": "ok"}
    """
    return {"status": "ok"}


@app.post("/predict")
def predict(req: PredictRequest):
    """
    Endpoint suy luan chinh.

    Dau vao : JSON {"features": [f1, f2, ..., f12]}
    Dau ra  : JSON {"prediction": <0|1|2>, "label": <"thap"|"trung_binh"|"cao">}

    Thu tu 12 dac trung (khop voi thu tu trong FEATURE_NAMES cua test):
        fixed_acidity, volatile_acidity, citric_acid, residual_sugar,
        chlorides, free_sulfur_dioxide, total_sulfur_dioxide, density,
        pH, sulphates, alcohol, wine_type
    """
    if len(req.features) != 12:
        raise HTTPException(
            status_code=400,
            detail="Expected 12 features (wine quality)"
        )

    if model is None:
        raise HTTPException(status_code=500, detail="Model is not loaded")

    pred = int(model.predict([req.features])[0])
    label_map = {0: "thap", 1: "trung_binh", 2: "cao"}
    label = label_map.get(pred, "khong_xac_dinh")

    return {"prediction": pred, "label": label}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

