import pandas as pd
from loguru import logger


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Veriyi temizler ve temizlenmiş DataFrame'i döndürür.
    """
    logger.info("Veri temizleme başladı.")

    df = df.copy()
    original_rows = len(df)

    # Tamamen boş satırları kaldır
    df = df.dropna(how="all")
    after_dropna = len(df)

    # Metin sütunlarındaki baş/son boşlukları temizle
    for col in ("Product", "Region"):
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

    # Tekrar eden kayıtları kaldır
    df = df.drop_duplicates().reset_index(drop=True)
    final_rows = len(df)

    logger.info(f"Başlangıç satır sayısı: {original_rows}")
    logger.info(f"Boş satır silinen: {original_rows - after_dropna}")
    logger.info(f"Tekrarlı kayıt silinen: {after_dropna - final_rows}")
    logger.info(f"Kalan satır sayısı: {final_rows}")
    logger.info("Veri temizleme tamamlandı.")

    return df