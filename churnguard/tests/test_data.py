import pandas as pd

from churnguard.data import load_data, preprocess

EXPECTED_COLUMNS = [
    "customerID",
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
    "Churn",
]


def make_raw_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customerID": ["001", "002", "003", "004"],
            "gender": ["Female", "Male", "Female", "Male"],
            "SeniorCitizen": [0, 1, 0, 1],
            "Partner": ["Yes", "No", "Yes", "No"],
            "Dependents": ["No", "No", "Yes", "No"],
            "tenure": [1, 12, 24, 36],
            "PhoneService": ["No", "Yes", "Yes", "Yes"],
            "MultipleLines": ["No phone service", "No", "Yes", "No"],
            "InternetService": ["DSL", "Fiber optic", "DSL", "No"],
            "OnlineSecurity": ["No", "No", "Yes", "No internet service"],
            "OnlineBackup": ["Yes", "No", "Yes", "No internet service"],
            "DeviceProtection": ["No", "Yes", "No", "No internet service"],
            "TechSupport": ["No", "No", "Yes", "No internet service"],
            "StreamingTV": ["No", "Yes", "No", "No internet service"],
            "StreamingMovies": ["No", "Yes", "Yes", "No internet service"],
            "Contract": ["Month-to-month", "One year", "Two year", "Month-to-month"],
            "PaperlessBilling": ["Yes", "No", "Yes", "No"],
            "PaymentMethod": [
                "Electronic check",
                "Mailed check",
                "Bank transfer (automatic)",
                "Credit card (automatic)",
            ],
            "MonthlyCharges": [29.85, 56.95, 53.85, 42.3],
            "TotalCharges": ["29.85", "684.1", "1292.4", "1522.8"],
            "Churn": ["No", "Yes", "No", "Yes"],
        }
    )


def test_load_data_returns_dataframe(tmp_path) -> None:
    csv_path = tmp_path / "telco_churn.csv"
    make_raw_dataframe().to_csv(csv_path, index=False)

    df = load_data(str(csv_path))

    assert isinstance(df, pd.DataFrame)
    assert df.shape == (4, 21)


def test_load_data_has_expected_columns(tmp_path) -> None:
    csv_path = tmp_path / "telco_churn.csv"
    make_raw_dataframe().to_csv(csv_path, index=False)

    df = load_data(str(csv_path))

    assert list(df.columns) == EXPECTED_COLUMNS


def test_preprocess_returns_features_and_target() -> None:
    df = make_raw_dataframe()

    X, y = preprocess(df)

    assert "Churn" not in X.columns
    assert "customerID" not in X.columns
    assert len(X) == len(y)
    assert set(y.unique()) == {0, 1}


def test_preprocess_handles_missing_total_charges() -> None:
    df = make_raw_dataframe()
    df.loc[0, "TotalCharges"] = " "

    X, y = preprocess(df)

    assert len(X) == 3
    assert len(y) == 3
    assert X["TotalCharges"].isna().sum() == 0
