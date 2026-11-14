import pandas as pd

from src.data_cleaner import clean_data


def test_clean_data_removes_empty_rows():
    df = pd.DataFrame({
        "Date": ["2026-01-01", None],
        "Product": ["Brake Pad", None],
        "Region": ["İzmir", None],
        "Quantity": [10, None],
        "UnitPrice": [100, None],
        "UnitCost": [60, None],
    })

    result = clean_data(df)

    assert len(result) == 1


def test_clean_data_removes_duplicates():
    df = pd.DataFrame({
        "Date": ["2026-01-01", "2026-01-01"],
        "Product": ["Brake Pad", "Brake Pad"],
        "Region": ["İzmir", "İzmir"],
        "Quantity": [10, 10],
        "UnitPrice": [100, 100],
        "UnitCost": [60, 60],
    })

    result = clean_data(df)

    assert len(result) == 1


def test_clean_data_strips_whitespace_before_dedup():
    df = pd.DataFrame({
        "Date": ["2026-01-01", "2026-01-01"],
        "Product": ["Brake Pad ", "Brake Pad"],
        "Region": [" İzmir", "İzmir"],
        "Quantity": [10, 10],
        "UnitPrice": [100, 100],
        "UnitCost": [60, 60],
    })

    result = clean_data(df)

    assert len(result) == 1
    assert result.iloc[0]["Product"] == "Brake Pad"
    assert result.iloc[0]["Region"] == "İzmir"