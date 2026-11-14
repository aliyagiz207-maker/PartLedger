import pandas as pd
import pytest

from src.validator import validate_dataframe


def build_valid_df():
    return pd.DataFrame({
        "Date": ["2026-01-01", "2026-01-02"],
        "Product": ["Brake Pad", "Oil Filter"],
        "Region": ["İzmir", "Manisa"],
        "Quantity": [10, 5],
        "UnitPrice": [100, 50],
        "UnitCost": [60, 30],
    })


def test_valid_dataframe_does_not_raise():
    df = build_valid_df()
    result = validate_dataframe(df)
    assert pd.api.types.is_datetime64_any_dtype(result["Date"])


def test_empty_dataframe_raises():
    df = pd.DataFrame(columns=[
        "Date", "Product", "Region",
        "Quantity", "UnitPrice", "UnitCost",
    ])

    with pytest.raises(ValueError, match="boş"):
        validate_dataframe(df)


def test_missing_column_raises():
    df = build_valid_df().drop(columns=["Region"])

    with pytest.raises(ValueError, match="Eksik sütun"):
        validate_dataframe(df)


def test_non_numeric_quantity_raises():
    df = build_valid_df()
    df["Quantity"] = ["ten", "five"]

    with pytest.raises(ValueError, match="Sayısal"):
        validate_dataframe(df)


def test_invalid_date_raises():
    df = build_valid_df()
    df["Date"] = ["2026-01-01", "not-a-date"]

    with pytest.raises(ValueError, match="tarih"):
        validate_dataframe(df)


def test_negative_quantity_raises():
    df = build_valid_df()
    df["Quantity"] = [10, -5]

    with pytest.raises(ValueError, match="Negatif"):
        validate_dataframe(df)


def test_negative_unit_price_raises():
    df = build_valid_df()
    df["UnitPrice"] = [100, -50]

    with pytest.raises(ValueError, match="Negatif"):
        validate_dataframe(df)


def test_negative_unit_cost_raises():
    df = build_valid_df()
    df["UnitCost"] = [-60, 30]

    with pytest.raises(ValueError, match="Negatif"):
        validate_dataframe(df)


def test_zero_quantity_does_not_raise():
    df = build_valid_df()
    df["Quantity"] = [0, 5]

    validate_dataframe(df)


def test_partial_nan_in_numeric_column_raises():
    df = build_valid_df()
    df["UnitPrice"] = [100.0, float("nan")]

    with pytest.raises(ValueError, match="Eksik \\(boş\\) sayısal"):
        validate_dataframe(df)


def test_missing_region_raises():
    df = build_valid_df()
    df["Region"] = ["İzmir", None]

    with pytest.raises(ValueError, match="Eksik \\(boş\\) metin"):
        validate_dataframe(df)


def test_blank_product_raises():
    df = build_valid_df()
    df["Product"] = ["   ", "Oil Filter"]

    with pytest.raises(ValueError, match="Eksik \\(boş\\) metin"):
        validate_dataframe(df)


def test_none_dataframe_raises():
    with pytest.raises(ValueError, match="boş"):
        validate_dataframe(None)