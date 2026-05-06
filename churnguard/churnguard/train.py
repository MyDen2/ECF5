# from typing import Any

# import pandas as pd
# from sklearn.compose import ColumnTransformer
# from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
# from sklearn.linear_model import LogisticRegression
# from sklearn.pipeline import Pipeline
# from sklearn.preprocessing import OneHotEncoder, StandardScaler

# NUMERIC_COLUMNS = ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen"]


# def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
#     """Construit un transformeur pour les colonnes numériques et catégorielles."""
#     categorical_columns = [column for column in X.columns if column not in NUMERIC_COLUMNS]

#     return ColumnTransformer(
#         transformers=[
#             ("num", StandardScaler(), NUMERIC_COLUMNS),
#             ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_columns),
#         ]
#     )


# def build_classifier(model_name: str, params: dict[str, Any]) -> Any:
#     """Construis un classifier à partir du nom raccourci du model."""
#     if model_name == "rf":
#         return RandomForestClassifier(random_state=42, n_jobs=-1, **params)

#     if model_name == "logreg":
#         return LogisticRegression(random_state=42, max_iter=1000, **params)

#     if model_name == "gb":
#         return GradientBoostingClassifier(random_state=42, **params)

#     msg = f"Unsupported model_name: {model_name}. Use 'rf', 'logreg' or 'gb'."
#     raise ValueError(msg)


# def train_model(
#     X: pd.DataFrame,
#     y: pd.Series,
#     model_name: str = "rf",
#     params: dict[str, Any] | None = None,
# ) -> Pipeline:
#     """Entraine le pipeline and retourne le modèle."""
#     model_params = params or {}

#     pipeline = Pipeline(
#         steps=[
#             ("prep", build_preprocessor(X)),
#             ("clf", build_classifier(model_name, model_params)),
#         ]
#     )

#     pipeline.fit(X, y)
#     return pipeline


# """Model training and MLflow logging utilities."""

# from typing import Any

# import mlflow
# import mlflow.sklearn
# import pandas as pd
# from mlflow.models import infer_signature
# from sklearn.compose import ColumnTransformer
# from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
# from sklearn.linear_model import LogisticRegression
# from sklearn.pipeline import Pipeline
# from sklearn.preprocessing import OneHotEncoder, StandardScaler

# from churnguard.evaluate import compute_metrics

# NUMERIC_COLUMNS = ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen"]


# def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
#     """Build a preprocessing transformer for numeric and categorical columns."""
#     categorical_columns = [column for column in X.columns if column not in NUMERIC_COLUMNS]

#     return ColumnTransformer(
#         transformers=[
#             ("num", StandardScaler(), NUMERIC_COLUMNS),
#             ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_columns),
#         ]
#     )


# def build_classifier(model_name: str, params: dict[str, Any]) -> Any:
#     """Build a classifier from its short model name."""
#     if model_name == "rf":
#         return RandomForestClassifier(random_state=42, n_jobs=-1, **params)

#     if model_name == "logreg":
#         return LogisticRegression(random_state=42, max_iter=1000, **params)

#     if model_name == "gb":
#         return GradientBoostingClassifier(random_state=42, **params)

#     msg = f"Unsupported model_name: {model_name}. Use 'rf', 'logreg' or 'gb'."
#     raise ValueError(msg)


# def train_model(
#     X: pd.DataFrame,
#     y: pd.Series,
#     model_name: str = "rf",
#     params: dict[str, Any] | None = None,
# ) -> Pipeline:
#     """Train a scikit-learn pipeline and return the fitted model."""
#     model_params = params or {}

#     pipeline = Pipeline(
#         steps=[
#             ("prep", build_preprocessor(X)),
#             ("clf", build_classifier(model_name, model_params)),
#         ]
#     )

#     pipeline.fit(X, y)
#     return pipeline


# def log_model_to_mlflow(
#     model: Pipeline,
#     model_name: str,
#     params: dict[str, Any],
#     metrics: dict[str, float],
#     X_example: pd.DataFrame,
# ) -> str:
#     """Log a trained model, parameters, metrics, signature and input example to MLflow."""
#     predictions = model.predict(X_example)
#     signature = infer_signature(X_example, predictions)

#     with mlflow.start_run(run_name=model_name) as run:
#         mlflow.log_params(params)
#         mlflow.log_metrics(metrics)

#         mlflow.sklearn.log_model(
#             sk_model=model,
#             artifact_path="model",
#             signature=signature,
#             input_example=X_example.head(5),
#         )

#         return run.info.run_id


# def train_and_log_model(
#     X_train: pd.DataFrame,
#     y_train: pd.Series,
#     X_test: pd.DataFrame,
#     y_test: pd.Series,
#     model_name: str,
#     params: dict[str, Any],
# ) -> dict[str, float]:
#     """Train a model, evaluate it and log the run to MLflow."""
#     model = train_model(X_train, y_train, model_name=model_name, params=params)
#     metrics = compute_metrics(model, X_test, y_test)

#     log_model_to_mlflow(
#         model=model,
#         model_name=model_name,
#         params={"model_name": model_name, **params},
#         metrics=metrics,
#         X_example=X_test.head(5),
#     )

#     return metrics


# def train_three_models(
#     X_train: pd.DataFrame,
#     y_train: pd.Series,
#     X_test: pd.DataFrame,
#     y_test: pd.Series,
# ) -> dict[str, dict[str, float]]:
#     """Train and log LogisticRegression, RandomForest and GradientBoosting models."""
#     models = {
#         "logreg": {"C": 1.0},
#         "rf": {"n_estimators": 200, "max_depth": 10},
#         "gb": {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 3},
#     }

#     results = {}

#     for model_name, params in models.items():
#         results[model_name] = train_and_log_model(
#             X_train=X_train,
#             y_train=y_train,
#             X_test=X_test,
#             y_test=y_test,
#             model_name=model_name,
#             params=params,
#         )

#     return results

"""Model training, MLflow logging and registry utilities."""

import argparse
from pathlib import Path
from typing import Any

import mlflow
import mlflow.pyfunc
import mlflow.sklearn
import pandas as pd
from mlflow.models import infer_signature
from mlflow.tracking import MlflowClient
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from churnguard.data import load_data, preprocess, split_data
from churnguard.evaluate import compute_metrics

NUMERIC_COLUMNS = ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen"]
REGISTERED_MODEL_NAME = "churnguard"


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    """Construit un transformeur pour les colonnes numériques et catégorielles."""
    categorical_columns = [column for column in X.columns if column not in NUMERIC_COLUMNS]
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_COLUMNS),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_columns),
        ]
    )


def build_classifier(model_name: str, params: dict[str, Any]) -> Any:
    """Construis un classifier à partir du nom raccourci du model."""
    if model_name == "rf":
        return RandomForestClassifier(random_state=42, n_jobs=-1, **params)
    if model_name == "logreg":
        return LogisticRegression(random_state=42, max_iter=1000, **params)
    if model_name == "gb":
        return GradientBoostingClassifier(random_state=42, **params)

    raise ValueError(f"Unsupported model_name: {model_name}")


def train_model(
    X: pd.DataFrame,
    y: pd.Series,
    model_name: str = "rf",
    params: dict[str, Any] | None = None,
) -> Pipeline:
    """Entraine le pipeline and retourne le modèle."""
    model_params = params or {}
    pipeline = Pipeline(
        steps=[
            ("prep", build_preprocessor(X)),
            ("clf", build_classifier(model_name, model_params)),
        ]
    )
    pipeline.fit(X, y)
    return pipeline


def log_model_to_mlflow(
    model: Pipeline,
    model_name: str,
    params: dict[str, Any],
    metrics: dict[str, float],
    X_example: pd.DataFrame,
    register: bool = False,
) -> str:
    """Log modèle entrainé sur  MLflow et option enregistrement."""
    predictions = model.predict(X_example)
    signature = infer_signature(X_example, predictions)

    with mlflow.start_run(run_name=model_name) as run:
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            signature=signature,
            input_example=X_example.head(5),
            registered_model_name=REGISTERED_MODEL_NAME if register else None,
        )

        return run.info.run_id


def promote_latest_model_to_production(model_name: str = REGISTERED_MODEL_NAME) -> str:
    """Promote the latest registered model version to Production."""
    client = MlflowClient()

    versions = client.search_model_versions(f"name='{model_name}'")
    latest_version = max(versions, key=lambda version: int(version.version))

    client.transition_model_version_stage(
        name=model_name,
        version=latest_version.version,
        stage="Staging",
        archive_existing_versions=True,
    )

    client.transition_model_version_stage(
        name=model_name,
        version=latest_version.version,
        stage="Production",
        archive_existing_versions=True,
    )

    return str(latest_version.version)


def load_production_model(model_name: str = REGISTERED_MODEL_NAME) -> Any:
    """Charge le modèle de production depuis le registre MLflow."""
    return mlflow.pyfunc.load_model(f"models:/{model_name}/Production")


def train_and_log_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    model_name: str,
    params: dict[str, Any],
    register: bool = False,
) -> dict[str, float]:
    """Entraînement, évaluation, log et option enregistrement du modèle."""
    model = train_model(X_train, y_train, model_name=model_name, params=params)
    metrics = compute_metrics(model, X_test, y_test)

    log_model_to_mlflow(
        model=model,
        model_name=model_name,
        params={"model_name": model_name, **params},
        metrics=metrics,
        X_example=X_test.head(5),
        register=register,
    )

    return metrics


def main() -> None:
    """Exécute l'entraînement du modèle depuis la ligne de commande."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["rf", "logreg", "gb"], default="rf")
    parser.add_argument("--register", action="store_true")
    parser.add_argument("--tracking-uri", default="http://127.0.0.1:5000")
    parser.add_argument("--data-path", default="data/telco_churn.csv")
    args = parser.parse_args()

    mlflow.set_tracking_uri(args.tracking_uri)
    mlflow.set_experiment("churnguard")

    data_path = Path(args.data_path)
    df = load_data(str(data_path))
    X, y = preprocess(df)
    X_train, X_test, y_train, y_test = split_data(X, y)

    default_params: dict[str, dict[str, Any]] = {
        "rf": {"n_estimators": 200, "max_depth": 10},
        "logreg": {"C": 1.0},
        "gb": {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 3},
    }

    metrics = train_and_log_model(
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
        model_name=args.model,
        params=default_params[args.model],
        register=args.register,
    )

    print(metrics)

    if args.register:
        version = promote_latest_model_to_production()
        print(f"Registered model '{REGISTERED_MODEL_NAME}' promoted to Production, version {version}")

        model = load_production_model()
        print(f"Production model loaded successfully: {model}")


if __name__ == "__main__":
    main()