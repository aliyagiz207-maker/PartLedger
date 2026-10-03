import pandas as pd
from pathlib import Path
from src import pdf_report
from src.pdf_report import generate_pdf_report

def test_generate_pdf_creates_file(tmp_path, monkeypatch):
    # Gerçek proje dizinini buluyoruz (Fontlar ve logoların okunabilmesi için)
    real_root = Path(pdf_report.__file__).resolve().parent.parent
    
    # Çıktıların (PDF) geçici test klasörüne (tmp_path) gitmesi için yönlendirme yapıyoruz
    monkeypatch.setattr(pdf_report, "get_application_root", lambda: tmp_path)
    
    # Fontların doğru klasörden okunabilmesi için resource_root'u gerçek dizine sabitliyoruz
    monkeypatch.setattr(pdf_report, "get_resource_root", lambda: real_root)
    
    kpis = {"Total Quantity": 10, "Total Revenue": 1000, "Profit Margin": 40.0}
    region_summary = pd.DataFrame({"Region": ["İzmir"], "Revenue": [1000], "Profit": [400], "Margin": [40.0]})
    product_summary = pd.DataFrame({"Product": ["Brake Pad"], "Revenue": [1000], "Profit": [400], "Margin": [40.0]})
    
    # DÜZELTME: "Margin" sütunu eklendi.
    monthly_summary = pd.DataFrame({"Month": ["2026-01"], "Revenue": [1000], "Profit": [400], "Margin": [40.0]})
    
    config = {
        "logo_path": "non_existent_logo.png",
        "dashboard_title": "PartLedger Test PDF",
        "company_name": "Terakki Test",
        "currency": "₺"
    }
    
    generate_pdf_report(kpis, region_summary, product_summary, monthly_summary, config)
    
    output_file = tmp_path / "data" / "output" / "PartLedger_Rapor.pdf"
    assert output_file.exists(), "PDF dosyası oluşturulamadı."
    assert output_file.stat().st_size > 0, "PDF dosyası boş."