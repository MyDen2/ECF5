import pandas as pd
from sklearn.pipeline import Pipeline

from churnguard.evaluate import compute_metrics
from churnguard.train import train_model


def make_training_dataframe() -> tuple[pd.DataFrame, pd.Series]:
    X = pd.DataFrame(
        {
            "gender": ["Female", "Male", "Female", "Male", "Female", "Male"],
            "SeniorCitizen": [0, 1, 0, 1, 0, 1],
            "Partner": ["Yes", "No", "Yes", "No", "Yes", "No"],
            "Dependents": ["No", "No", "Yes", "No", "Yes", "No"],
            "tenure": [1, 12, 24, 36, 48, 60],
            "PhoneService": ["No", "Yes", "Yes", "Yes", "No", "Yes"],
            "MultipleLines": ["No phone service", "No", "Yes", "No", "No phone service", "Yes"],
            "InternetService": ["DSL", "Fiber optic", "DSL", "No", "DSL", "Fiber optic"],
            "OnlineSecurity": ["No", "No", "Yes", "No internet service", "Yes", "No"],
            "OnlineBackup": ["Yes", "No", "Yes", "No internet service", "Yes", "No"],
            "DeviceProtection": ["No", "Yes", "No", "No internet service", "Yes", "No"],
            "TechSupport": ["No", "No", "Yes", "No internet service", "Yes", "No"],
            "StreamingTV": ["No", "Yes", "No", "No internet service", "Yes", "No"],
            "StreamingMovies": ["No", "Yes", "Yes", "No internet service", "Yes", "No"],
            "Contract": [
                "Month-to-month",
                "One year",
                "Two year",
                "Month-to-month",
                "Two year",
                "One year",
            ],
            "PaperlessBilling": ["Yes", "No", "Yes", "No", "Yes", "No"],
            "PaymentMethod": [
                "Electronic check",
                "Mailed check",
                "Bank transfer (automatic)",
                "Credit card (automatic)",
                "Electronic check",
                "Mailed check",
            ],
            "MonthlyCharges": [29.85, 56.95, 53.85, 42.3, 70.2, 88.4],
            "TotalCharges": [29.85, 684.1, 1292.4, 1522.8, 3369.6, 5304.0],
        }
    )
    y = pd.Series([0, 1, 0, 1, 0, 1])
    return X, y


def test_train_model_returns_fitted_pipeline() -> None:
    X, y = make_training_dataframe()

    model = train_model(X, y, model_name="rf", params={"n_estimators": 10, "max_depth": 3})
    predictions = model.predict(X)

    assert isinstance(model, Pipeline)
    assert len(predictions) == len(y)


def test_compute_metrics_returns_expected_keys() -> None:
    X, y = make_training_dataframe()
    model = train_model(X, y, model_name="rf", params={"n_estimators": 10, "max_depth": 3})

    metrics = compute_metrics(model, X, y)

    assert set(metrics.keys()) == {"accuracy", "precision", "recall", "f1", "roc_auc"}
    assert all(isinstance(value, float) for value in metrics.values())