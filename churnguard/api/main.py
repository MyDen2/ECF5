"""Application FastAPI pour les prédictions ChurnGuard."""

import os
from contextlib import asynccontextmanager
from typing import Any

import mlflow
import mlflow.pyfunc
import pandas as pd
from fastapi import FastAPI, HTTPException
from mlflow.tracking import MlflowClient
from pydantic import BaseModel, ConfigDict, Field

MODEL_NAME = "churnguard"
MODEL_STAGE = "Production"
MODEL_URI = f"models:/{MODEL_NAME}/{MODEL_STAGE}"

model: Any | None = None
model_version: str = "unknown"


class CustomerFeatures(BaseModel):
    """Features d'entrée de l'utilisateur pour la prédiction du churn."""

    model_config = ConfigDict(extra="forbid")

    gender: str
    SeniorCitizen: int = Field(ge=0, le=1)
    Partner: str
    Dependents: str
    tenure: int = Field(ge=0)
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float = Field(ge=0)
    TotalCharges: float = Field(ge=0)


class PredictionResponse(BaseModel):
    """Réponse retournée par l'API."""

    churn: bool
    probability: float = Field(ge=0.0, le=1.0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Charge le modèle de production MLflow dès le démarrage."""
    global model, model_version

    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"))

    try:
        model = mlflow.sklearn.load_model(MODEL_URI)

        client = MlflowClient()
        versions = client.get_latest_versions(MODEL_NAME, stages=[MODEL_STAGE])
        if versions:
            model_version = versions[0].version

    except Exception as exc:
        model = None
        model_version = "unavailable"
        print(f"Model loading failed: {exc}")

    yield


app = FastAPI(title="ChurnGuard API", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    """Retourne le health status de l'API et du modèle."""
    return {
        "status": "ok",
        "model": MODEL_NAME,
        "version": model_version,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(customer: CustomerFeatures) -> PredictionResponse:
    """Prediction du churn pour un utilisateur."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    df = pd.DataFrame([customer.model_dump()])
    probability = float(model.predict_proba(df)[0][1])

    return PredictionResponse(
        churn=probability >= 0.5,
        probability=probability,
    )


@app.post("/predict/batch", response_model=list[PredictionResponse])
def predict_batch(customers: list[CustomerFeatures]) -> list[PredictionResponse]:
    """Prediction du churn un ensemble d'utilisateurs."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if not customers:
        raise HTTPException(status_code=400, detail="Batch cannot be empty")

    if len(customers) > 100:
        raise HTTPException(status_code=400, detail="Batch size cannot exceed 100")

    df = pd.DataFrame([customer.model_dump() for customer in customers])
    probabilities = model.predict_proba(df)[:, 1]

    return [
        PredictionResponse(
            churn=float(probability) >= 0.5,
            probability=float(probability),
        )
        for probability in probabilities
    ]


# 422 est géré automatiquement par pydantic et fastapi.
