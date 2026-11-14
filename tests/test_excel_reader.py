"""
tests/test_excel_reader.py
Chunk destekli okuma katmanının birim testleri.
"""
import pandas as pd
import pytest

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
    df1 = pd.DataFrame({"Urun": ["A", "B"], "Ciro": [100, 200]})
    df2 = pd.DataFrame({"Urun": ["C", "D"], "Ciro": [300, 400]})

    df1.to_csv(tmp_path / "veri_test.csv", index=False)
    df2.to_excel(tmp_path / "veri_test.xlsx", index=False)

    sonuc = read_and_combine(str(tmp_path), chunk_size=1)

    assert sonuc is not None
    assert len(sonuc) == 4
    assert "Urun" in sonuc.columns
    assert "Ciro" in sonuc.columns


def test_turkish_cp1254_semicolon_csv(tmp_path):
    """Türkçe Excel'den çıkan cp1254 kodlamalı ve ';' ayraçlı CSV dosyalarını doğru okumalıdır."""
    csv_text = (
        "Date;Product;Region;Quantity;UnitPrice;UnitCost\n"
        "2026-01-15;Fren Balatası;İzmir;10;250;150\n"
        "2026-01-16;Yağ Filtresi;Muğla;5;120;70\n"
    )
    csv_file = tmp_path / "turkce_satis.csv"
    csv_file.write_bytes(csv_text.encode("cp1254"))

    sonuc = read_and_combine(tmp_path, chunk_size=1)

    assert sonuc is not None
    assert len(sonuc) == 2
    assert list(sonuc["Region"]) == ["İzmir", "Muğla"]
    assert list(sonuc["Product"]) == ["Fren Balatası", "Yağ Filtresi"]


def test_corrupt_binary_files_are_skipped_safely(tmp_path):
    """Uzantısı değiştirilmiş sahte/ikili dosyalar sistemi çökertmeden atlanmalıdır."""
    fake_csv = tmp_path / "bozuk_veri.csv"
    fake_xlsx = tmp_path / "sahte_veri.xlsx"
    fake_csv.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00corrupt_csv")
    fake_xlsx.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00corrupt_xlsx")

    sonuc = read_and_combine(tmp_path)
    assert sonuc is None