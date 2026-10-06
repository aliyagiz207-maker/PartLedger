"""
tests/test_excel_reader.py
Chunk destekli yeni okuma katmanının birim testleri.
"""
import pytest
import pandas as pd
from pathlib import Path
from src.excel_reader import read_and_combine

def test_invalid_directory():
    """Var olmayan bir klasör yolunda sistemin çökmeden FileNotFoundError fırlatması gerekir."""
    with pytest.raises(FileNotFoundError):
        read_and_combine("sistemde_asla_olmayan_hayali_bir_dizin")

def test_empty_directory(tmp_path):
    """Geçerli ama içi boş bir klasör verildiğinde hata fırlatmak yerine None dönmelidir."""
    result = read_and_combine(str(tmp_path))
    assert result is None

def test_successful_read_and_combine(tmp_path):
    """CSV ve Excel dosyalarını bulup, chunk limitlerinde başarıyla okuyup birleştirmelidir."""
    # tmp_path, pytest'in bizim için anlık oluşturup test bitince sildiği güvenli bir sanal klasördür.
    
    # İki farklı test verisi oluşturuyoruz
    df1 = pd.DataFrame({"Urun": ["A", "B"], "Ciro": [100, 200]})
    df2 = pd.DataFrame({"Urun": ["C", "D"], "Ciro": [300, 400]})
    
    # Biri CSV, diğeri Excel olarak kaydediliyor
    df1.to_csv(tmp_path / "veri_test.csv", index=False)
    df2.to_excel(tmp_path / "veri_test.xlsx", index=False)
    
    # Yeni motoru çalıştırıyoruz (chunk_size = 1 diyerek limiti bilerek daraltıyoruz ki döngü zorlansın)
    sonuc = read_and_combine(str(tmp_path), chunk_size=1)
    
    # Sistemin doğru çalıştığını kanıtlayan şartlar
    assert sonuc is not None
    assert len(sonuc) == 4  # Toplam 4 satır veri olmalı
    assert "Urun" in sonuc.columns
    assert "Ciro" in sonuc.columns