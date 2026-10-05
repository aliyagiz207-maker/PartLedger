import pandas as pd
import random
from datetime import datetime, timedelta
import os

desktop = os.path.join(os.path.expanduser("~"), "Desktop", "PartLedger_Demo_Verileri")
os.makedirs(desktop, exist_ok=True)

regions = ["İzmir", "Manisa", "Aydın", "Denizli", "Muğla"]
products = {
    "Brake Pad": (893.00, 540.00),
    "Engine Oil": (620.00, 410.00),
    "Clutch Kit": (2750.00, 1850.00),
    "Battery": (4100.00, 3300.00),
    "Brake Disc": (1450.00, 980.00),
    "Spark Plug": (190.00, 95.00),
    "Air Filter": (280.00, 150.00),
    "Cabin Filter": (260.00, 140.00),
    "Wiper Blade": (370.00, 210.00),
    "Oil Filter": (320.00, 180.00)
}

def create_monthly_data(month, filename):
    data = []
    start_date = datetime(2026, month, 1)
    days_in_month = 28 if month == 2 else 31
    
    for _ in range(140):  
        day = random.randint(1, days_in_month)
        date = start_date + timedelta(days=day-1)
        region = random.choice(regions)
        product = random.choice(list(products.keys()))
        price, cost = products[product]
        qty = random.randint(10, 80)
        
        # DÜZELTME: Tarihi metne çevirmeden, doğrudan Python "datetime" objesi olarak ekliyoruz!
        data.append([date, product, region, qty, price, cost])
        
    df = pd.DataFrame(data, columns=["Date", "Product", "Region", "Quantity", "UnitPrice", "UnitCost"])
    
    # Verileri tarihe göre sırala
    df = df.sort_values(by="Date").reset_index(drop=True)

    filepath = os.path.join(desktop, filename)
    df.to_excel(filepath, index=False)
    print(f"Oluşturuldu: {filename}")

print("Sunum için şirket verileri üretiliyor (Gerçek Excel Tarih Formatı)...")
create_monthly_data(1, "2026_01_Ocak_Satis.xlsx")
create_monthly_data(2, "2026_02_Subat_Satis.xlsx")
create_monthly_data(3, "2026_03_Mart_Satis.xlsx")
print(f"\nTüm veriler hazır! Klasör yolu: {desktop}")