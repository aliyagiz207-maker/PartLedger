"""
src/excel_reader.py
Büyük veri setleri için bellek optimize edilmiş (Chunking) okuma ve birleştirme katmanı.
"""
from pathlib import Path
from typing import Optional, Tuple, Union

import pandas as pd
from loguru import logger

_BINARY_SIGNATURES = (
    b"\x89PNG\r\n\x1a\n",
    b"\xff\xd8\xff",
    b"PK\x03\x04",
    b"%PDF-",
)


def _detect_csv_format(file_path: Path) -> Tuple[str, str]:
    """
    CSV dosyasının ikili (binary) olmadığını doğrular, karakter kodlamasını
    (UTF-8 / Windows-1254) ve ayraç karakterini (';' veya ',') tespit eder.
    """
    raw_bytes = file_path.read_bytes()[:4096]
    if not raw_bytes:
        raise ValueError("CSV dosyası tamamen boş.")

    if b"\x00" in raw_bytes or raw_bytes.startswith(_BINARY_SIGNATURES):
        raise ValueError("Dosya geçerli bir CSV değil (ikili/binary içerik tespit edildi).")

    detected_encoding = None
    decoded_sample = ""

    for encoding in ("utf-8-sig", "cp1254"):
        try:
            decoded_sample = raw_bytes.decode(encoding)
            detected_encoding = encoding
            break
        except UnicodeDecodeError:
            continue

    if detected_encoding is None:
        raise ValueError(
            "CSV dosyasının karakter kodlaması desteklenmiyor (UTF-8 veya Windows-1254 bekleniyor)."
        )

    first_line = ""
    for line in decoded_sample.splitlines():
        if line.strip():
            first_line = line
            break

    if "," not in first_line and ";" not in first_line:
        raise ValueError("CSV başlık satırında geçerli bir sütun ayracı (',' veya ';') bulunamadı.")

    delimiter = ";" if first_line.count(";") > first_line.count(",") else ","
    return detected_encoding, delimiter


def read_and_combine(
    input_dir: Union[str, Path],
    chunk_size: int = 50000,
) -> Optional[pd.DataFrame]:
    """
    Belirtilen dizindeki tüm CSV ve Excel dosyalarını okur ve birleştirir.
    Büyük CSV dosyaları bellek taşmasını (MemoryError) önlemek için chunk'lar halinde okunur.
    """
    target_path = Path(input_dir)

    if not target_path.exists():
        logger.error(f"KRİTİK HATA: Girdi dizini bulunamadı -> {input_dir}")
        raise FileNotFoundError(f"Dizin mevcut değil: {input_dir}")

    supported_extensions = {".csv", ".xlsx", ".xls"}
    files_to_read = sorted(
        f for f in target_path.iterdir()
        if f.is_file() and f.suffix.lower() in supported_extensions
    )

    if not files_to_read:
        logger.warning(
            f"UYARI: '{input_dir}' dizininde işlenecek geçerli bir Excel veya CSV dosyası bulunamadı."
        )
        return None

    logger.info(f"Toplam {len(files_to_read)} dosya sırayla işleme alınıyor...")
    data_frames = []

    for file_path in files_to_read:
        try:
            if file_path.suffix.lower() == ".csv":
                encoding, sep = _detect_csv_format(file_path)
                logger.debug(
                    f"Okunuyor (CSV - Chunk Modu, encoding={encoding}, sep='{sep}'): {file_path.name}"
                )
                for chunk in pd.read_csv(
                    file_path,
                    sep=sep,
                    encoding=encoding,
                    chunksize=chunk_size,
                    low_memory=False,
                ):
                    data_frames.append(chunk)
            else:
                logger.debug(f"Okunuyor (Excel): {file_path.name}")
                df = pd.read_excel(file_path, engine="openpyxl")
                data_frames.append(df)

        except Exception as e:
            logger.error(f"HATA: Dosya okuma başarısız ({file_path.name}). Sebep: {str(e)}")
            continue

    if not data_frames:
        logger.error("KRİTİK HATA: Dosyalar tarandı ancak hiçbirinden okunabilir veri çıkarılamadı.")
        return None

    logger.info("Tüm veri parçaları bellek üzerinde tek bir ana yapıya (DataFrame) birleştiriliyor...")
    final_df = pd.concat(data_frames, ignore_index=True)
    logger.success(
        f"Veri okuma ve birleştirme tamamlandı. Toplam işlenen satır sayısı: {len(final_df)}"
    )

    return final_df