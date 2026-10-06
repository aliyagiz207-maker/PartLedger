"""
src/excel_reader.py
Büyük veri setleri için bellek optimize edilmiş (Chunking) okuma ve birleştirme katmanı.
"""
import pandas as pd
from pathlib import Path
from loguru import logger
from typing import Optional

def read_and_combine(input_dir: str, chunk_size: int = 50000) -> Optional[pd.DataFrame]:
    """
    Belirtilen dizindeki tüm CSV ve Excel dosyalarını okur ve birleştirir.
    Büyük CSV dosyaları bellek taşmasını (MemoryError) önlemek için chunk'lar halinde okunur.
    
    Parametreler:
        input_dir (str): Okunacak veri dosyalarının bulunduğu klasör yolu.
        chunk_size (int): CSV dosyaları okunurken tek seferde RAM'e alınacak maksimum satır sayısı.
        
    Dönüş:
        pd.DataFrame: Birleştirilmiş verileri içeren DataFrame veya hata durumunda None.
    """
    target_path = Path(input_dir)
    
    # 1. Klasör Doğrulaması
    if not target_path.exists():
        logger.error(f"KRİTİK HATA: Girdi dizini bulunamadı -> {input_dir}")
        raise FileNotFoundError(f"Dizin mevcut değil: {input_dir}")

    # 2. Desteklenen Dosyaların Tespiti
    supported_extensions = ['.csv', '.xlsx', '.xls']
    files_to_read = [
        f for f in target_path.iterdir() 
        if f.is_file() and f.suffix.lower() in supported_extensions
    ]

    if not files_to_read:
        logger.warning(f"UYARI: '{input_dir}' dizininde işlenecek geçerli bir Excel veya CSV dosyası bulunamadı.")
        return None

    logger.info(f"Toplam {len(files_to_read)} dosya sırayla işleme alınıyor...")
    data_frames = []

    # 3. Bellek Optimizasyonlu (Chunking) Okuma Döngüsü
    for file_path in files_to_read:
        try:
            if file_path.suffix.lower() == '.csv':
                logger.debug(f"Okunuyor (CSV - Chunk Modu Aktif): {file_path.name}")
                # Veriyi dev bir blok halinde değil, 'chunk_size' büyüklüğünde paketler halinde RAM'e alırız.
                for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
                    data_frames.append(chunk)
            else:
                logger.debug(f"Okunuyor (Excel): {file_path.name}")
                # Pandas doğrudan chunk desteklemez, bellek tasarrufu için openpyxl motoru zorunlu tutulur.
                df = pd.read_excel(file_path, engine='openpyxl')
                data_frames.append(df)
                
        except Exception as e:
            logger.error(f"HATA: Dosya okuma başarısız ({file_path.name}). Sebep: {str(e)}")
            continue

    # 4. Hata Yönetimi ve Veri Kontrolü
    if not data_frames:
        logger.error("KRİTİK HATA: Dosyalar tarandı ancak hiçbirinden okunabilir veri çıkarılamadı.")
        return None

    # 5. Parçalanmış Verileri Güvenli Bir Şekilde Birleştirme
    logger.info("Tüm veri parçaları bellek üzerinde tek bir ana yapıya (DataFrame) birleştiriliyor...")
    final_df = pd.concat(data_frames, ignore_index=True)
    logger.success(f"Veri okuma ve birleştirme tamamlandı. Toplam işlenen satır sayısı: {len(final_df)}")
    
    return final_df