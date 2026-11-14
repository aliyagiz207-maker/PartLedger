import pandas as pd
from openpyxl import load_workbook

from src.kpi_calculator import calculate_kpis
from src.report_generator import generate_report


def test_generate_report_creates_excel(tmp_path):
    df = pd.DataFrame({
        "Date": pd.to_datetime(["2026-01-01"]),
        "Product": ["Brake Pad"],
        "Region": ["İzmir"],
        "Quantity": [10],
        "UnitPrice": [100.0],
        "UnitCost": [60.0],
    })
    kpis, region_summary, product_summary, monthly_summary, enriched_df = calculate_kpis(df)

    test_output = tmp_path / "Test_Dashboard.xlsx"
    config = {
        "output_file": str(test_output),
        "logo_path": "non_existent_logo.png",
        "dashboard_title": "PartLedger Test Dashboard",
        "company_name": "Terakki Test",
        "currency": "₺",
    }

    generate_report(kpis, region_summary, product_summary, monthly_summary, enriched_df, config)

    assert test_output.exists(), "Excel dosyası oluşturulamadı."
    wb = load_workbook(test_output)
    assert "Dashboard" in wb.sheetnames, "Dashboard sayfası eksik."
    assert "Detail Data" in wb.sheetnames, "Detail Data sayfası eksik."

    detail_headers = [cell.value for cell in wb["Detail Data"][1]]
    assert detail_headers == [
        "Date",
        "Product",
        "Region",
        "Quantity",
        "UnitPrice",
        "UnitCost",
        "Revenue",
        "Cost",
        "Profit",
    ]
    assert wb["Detail Data"]["G2"].value == 1000.0
    assert wb["Detail Data"]["H2"].value == 600.0
    assert wb["Detail Data"]["I2"].value == 400.0


def test_generate_report_handles_string_dates(tmp_path):
    df = pd.DataFrame({
        "Date": ["2026-01-01", "2026-01-15"],
        "Product": ["Brake Pad", "Oil Filter"],
        "Region": ["İzmir", "Manisa"],
        "Quantity": [10, 5],
        "UnitPrice": [100.0, 50.0],
        "UnitCost": [60.0, 30.0],
    })
    kpis, region_summary, product_summary, monthly_summary, enriched_df = calculate_kpis(df)

    test_output = tmp_path / "String_Date_Dashboard.xlsx"
    config = {
        "output_file": str(test_output),
        "logo_path": "non_existent_logo.png",
        "dashboard_title": "String Date Test",
        "company_name": "Terakki Test",
        "currency": "₺",
    }

    generate_report(kpis, region_summary, product_summary, monthly_summary, enriched_df, config)
    assert test_output.exists()