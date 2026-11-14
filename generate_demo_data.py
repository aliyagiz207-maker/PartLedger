import os
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

REGIONS = ["İzmir", "Manisa", "Aydın", "Denizli", "Muğla"]
PRODUCTS = {
    "Brake Pad": (893.00, 540.00),
    "Engine Oil": (620.00, 410.00),
    "Clutch Kit": (2750.00, 1850.00),
    "Battery": (4100.00, 3300.00),
    "Brake Disc": (1450.00, 980.00),
    "Spark Plug": (190.00, 95.00),
    "Air Filter": (280.00, 150.00),
    "Cabin Filter": (260.00, 140.00),
    "Wiper Blade": (370.00, 210.00),
    "Oil Filter": (320.00, 180.00),
}


def create_monthly_data(month: int, filename: str, output_dir: Path) -> Path:
    data = []
    start_date = datetime(2026, month, 1)
    days_in_month = 28 if month == 2 else 31

    for _ in range(140):
        day = random.randint(1, days_in_month)
        date = start_date + timedelta(days=day - 1)
        region = random.choice(REGIONS)
        product = random.choice(list(PRODUCTS.keys()))
        price, cost = PRODUCTS[product]
        qty = random.randint(10, 80)

        data.append([date, product, region, qty, price, cost])

    df = pd.DataFrame(
        data,
        columns=["Date", "Product", "Region", "Quantity", "UnitPrice", "UnitCost"],
    )
    df = df.sort_values(by="Date").reset_index(drop=True)

    filepath = output_dir / filename
    df.to_excel(filepath, index=False)
    print(f"Oluşturuldu: {filename}")
    return filepath


def main():
    desktop = Path(os.path.expanduser("~")) / "Desktop" / "PartLedger_Demo_Verileri"
    desktop.mkdir(parents=True, exist_ok=True)

    print("Sunum için şirket verileri üretiliyor (Gerçek Excel Tarih Formatı)...")
    create_monthly_data(1, "2026_01_Ocak_Satis.xlsx", desktop)
    create_monthly_data(2, "2026_02_Subat_Satis.xlsx", desktop)
    create_monthly_data(3, "2026_03_Mart_Satis.xlsx", desktop)
    print(f"\nTüm veriler hazır! Klasör yolu: {desktop}")


if __name__ == "__main__":
    main()