import pandas as pd

REQUIRED_COLUMNS = [
    "Date",
    "Product",
    "Region",
    "Quantity",
    "UnitPrice",
    "UnitCost",
]

NUMERIC_COLUMNS = [
    "Quantity",
    "UnitPrice",
    "UnitCost",
]

TEXT_COLUMNS = [
    "Product",
    "Region",
]


def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Excel/CSV dosyasındaki veriyi doğrular ve Date sütununu datetime tipine normalize eder.
    Sorun varsa açıklayıcı ValueError fırlatır.
    """
    if df is None or df.empty:
        raise ValueError("Excel dosyası boş.")

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Eksik sütun(lar): {', '.join(missing)}")

    # Sayısal olması gereken sütunlar gerçekten sayısal mı?
    non_numeric = [
        col for col in NUMERIC_COLUMNS
        if not pd.api.types.is_numeric_dtype(df[col])
    ]
    if non_numeric:
        raise ValueError(
            f"Sayısal olması gereken sütun(lar) sayısal değil: "
            f"{', '.join(non_numeric)}"
        )

    # Sayısal sütunlarda kısmi boş (NaN) hücre kontrolü
    null_numeric = [col for col in NUMERIC_COLUMNS if df[col].isna().any()]
    if null_numeric:
        raise ValueError(
            f"Eksik (boş) sayısal değer içeren sütun(lar): "
            f"{', '.join(null_numeric)}"
        )

    # Metin sütunlarında (Product, Region) boş / NaN değer kontrolü
    null_text = []
    for col in TEXT_COLUMNS:
        is_blank = df[col].isna() | (df[col].astype(str).str.strip() == "")
        if is_blank.any():
            null_text.append(col)
    if null_text:
        raise ValueError(
            f"Eksik (boş) metin değeri içeren sütun(lar): "
            f"{', '.join(null_text)}"
        )

    # Date sütunu tarihe çevrilebiliyor mu?
    parsed_dates = pd.to_datetime(df["Date"], errors="coerce")
    if parsed_dates.isna().any():
        invalid_count = int(parsed_dates.isna().sum())
        raise ValueError(
            f"Geçersiz tarih içeren {invalid_count} satır bulundu."
        )

    # CSV girdilerinde string kalan tarihleri downstream katmanlar için normalize et
    df["Date"] = parsed_dates

    # Negatif değer kontrolü
    negative_columns = [
        col for col in NUMERIC_COLUMNS
        if (df[col] < 0).any()
    ]
    if negative_columns:
        raise ValueError(
            f"Negatif değer içeren sütun(lar): "
            f"{', '.join(negative_columns)}"
        )

    return df