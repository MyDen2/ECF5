from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from churnguard.evaluate import compute_metrics
from churnguard.train import (
    build_classifier,
    build_preprocessor,
    log_model_to_mlflow,
    promote_latest_model_to_production,
    train_and_log_model,
    train_model,
)


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


def test_build_classifier_returns_logistic_regression() -> None:
    clf = build_classifier("logreg", {"C": 1.0})

    assert isinstance(clf, LogisticRegression)


def test_build_classifier_returns_random_forest() -> None:
    clf = build_classifier("rf", {"n_estimators": 10, "max_depth": 3})

    assert isinstance(clf, RandomForestClassifier)


def test_build_classifier_returns_gradient_boosting() -> None:
    clf = build_classifier("gb", {"n_estimators": 10, "max_depth": 2})

    assert isinstance(clf, GradientBoostingClassifier)


def test_build_classifier_raises_on_unknown_model() -> None:
    with pytest.raises(ValueError, match="Unsupported model_name"):
        build_classifier("unknown", {})


def test_build_preprocessor_returns_transformer() -> None:
    X, _ = make_training_dataframe()

    transformer = build_preprocessor(X)

    assert len(transformer.transformers) == 2


# ajout test mocké pour couvrir train_and_log_model sans lancer MLflow réel.


def test_train_and_log_model_returns_metrics() -> None:
    X, y = make_training_dataframe()

    with patch("churnguard.train.log_model_to_mlflow", return_value="run-id"):
        metrics = train_and_log_model(
            X_train=X,
            y_train=y,
            X_test=X,
            y_test=y,
            model_name="rf",
            params={"n_estimators": 10, "max_depth": 3},
            register=False,
        )

    assert set(metrics.keys()) == {"accuracy", "precision", "recall", "f1", "roc_auc"}


# ajout test mocké pour couvrir promote_latest_model_to_production sans lancer MLflow réel.


def test_promote_latest_model_to_production_returns_latest_version() -> None:
    with patch("churnguard.train.MlflowClient") as client_class:
        client = client_class.return_value
        client.search_model_versions.return_value = [
            SimpleNamespace(version="1"),
            SimpleNamespace(version="2"),
        ]

        version = promote_latest_model_to_production()

    assert version == "2"
    assert client.transition_model_version_stage.call_count == 2


def test_log_model_to_mlflow_calls_mlflow() -> None:
    """
    vérifiaction MLflow est appelé +
    les params sont log +
    les métriques sont log +
    le modèle est log
    """
    X, _ = make_training_dataframe()

    model = MagicMock()
    model.predict.return_value = [0, 1, 0, 1, 0]

    with (
        patch("churnguard.train.infer_signature", return_value="signature"),
        patch("churnguard.train.mlflow") as mlflow_mock,
    ):
        run_mock = MagicMock()
        run_mock.info.run_id = "run-id"
        mlflow_mock.start_run.return_value.__enter__.return_value = run_mock

        run_id = log_model_to_mlflow(
            model=model,
            model_name="rf",
            params={"n_estimators": 10},
            metrics={"accuracy": 0.9},
            X_example=X.head(5),
            register=False,
        )

    assert run_id == "run-id"
    mlflow_mock.start_run.assert_called_once_with(run_name="rf")
    mlflow_mock.log_params.assert_called_once_with({"n_estimators": 10})
    mlflow_mock.log_metrics.assert_called_once_with({"accuracy": 0.9})
    mlflow_mock.sklearn.log_model.assert_called_once()
