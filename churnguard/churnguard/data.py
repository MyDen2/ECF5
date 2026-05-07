from typing import cast

import pandas as pd
from sklearn.model_selection import train_test_split

TARGET_COLUMN = "Churn"
ID_COLUMN = "customerID"


def load_data(path: str) -> pd.DataFrame:
    """Charge le CSV brut"""
    return pd.read_csv(path)


def preprocess(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Fait le préprocessing et retourne X, y"""
    data = df.copy()

    data["TotalCharges"] = pd.to_numeric(data["TotalCharges"], errors="coerce")
    data = data.dropna()

    if ID_COLUMN in data.columns:
        data = data.drop(columns=[ID_COLUMN])

    y = (data[TARGET_COLUMN] == "Yes").astype(int)
    X = data.drop(columns=[TARGET_COLUMN])

    return X, y


def split_data(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Split les features et la target en ensemble de train and test"""
    return cast(
        tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series],
        train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state,
            stratify=y,
        ),
    )
