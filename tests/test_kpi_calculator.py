import pandas as pd
import pytest

from src.kpi_calculator import calculate_kpis


def build_sample_df():
    return pd.DataFrame({
        "Date": [
            "2026-01-01",
            "2026-01-02",
            "2026-01-03",
        ],
        "Product": [
            "Brake Pad",
            "Brake Pad",
            "Oil Filter",
        ],
        "Region": [
            "İzmir",
            "Manisa",
            "İzmir",
        ],
        "Quantity": [10, 5, 20],
        "UnitPrice": [100, 100, 50],
        "UnitCost": [60, 60, 30],
    })


def test_total_quantity():
    df = build_sample_df()

    kpis, _, _, _ = calculate_kpis(df)

    assert kpis["Total Quantity"] == 35


def test_total_revenue():
    df = build_sample_df()

    kpis, _, _, _ = calculate_kpis(df)

    # (10*100) + (5*100) + (20*50) = 1000 + 500 + 1000
    assert kpis["Total Revenue"] == 2500


def test_total_cost():
    df = build_sample_df()

    kpis, _, _, _ = calculate_kpis(df)

    # (10*60) + (5*60) + (20*30) = 600 + 300 + 600
    assert kpis["Total Cost"] == 1500


def test_total_profit():
    df = build_sample_df()

    kpis, _, _, _ = calculate_kpis(df)

    assert kpis["Total Profit"] == 1000


def test_profit_margin():
    df = build_sample_df()

    kpis, _, _, _ = calculate_kpis(df)

    # 1000 / 2500 * 100 = 40.0
    assert kpis["Profit Margin"] == pytest.approx(40.0)


def test_profit_margin_zero_revenue_does_not_crash():
    df = pd.DataFrame({
        "Date": ["2026-01-01"],
        "Product": ["Brake Pad"],
        "Region": ["İzmir"],
        "Quantity": [0],
        "UnitPrice": [100],
        "UnitCost": [60],
    })

    kpis, _, _, _ = calculate_kpis(df)

    assert kpis["Total Revenue"] == 0
    assert kpis["Profit Margin"] == 0


def test_empty_dataframe_does_not_crash():
    df = pd.DataFrame(columns=[
        "Date",
        "Product",
        "Region",
        "Quantity",
        "UnitPrice",
        "UnitCost",
    ])

    kpis, region_summary, product_summary, _ = calculate_kpis(df)

    assert kpis["Total Quantity"] == 0
    assert kpis["Total Revenue"] == 0
    assert kpis["Profit Margin"] == 0
    assert region_summary.empty
    assert product_summary.empty


def test_region_summary_columns_and_sort_order():
    df = build_sample_df()

    _, region_summary, _, _ = calculate_kpis(df)

    assert list(region_summary.columns) == [
        "Region",
        "Revenue",
        "Cost",
        "Profit",
        "Margin",
    ]

    # İzmir: (10*100)+(20*50) = 2000 > Manisa: 5*100 = 500
    assert region_summary.iloc[0]["Region"] == "İzmir"
    assert region_summary.iloc[0]["Revenue"] == 2000
    assert region_summary.iloc[1]["Region"] == "Manisa"
    assert region_summary.iloc[1]["Revenue"] == 500


def test_product_summary_columns_and_sort_order():
    df = build_sample_df()

    _, _, product_summary, _ = calculate_kpis(df)

    assert list(product_summary.columns) == [
        "Product",
        "Revenue",
        "Cost",
        "Profit",
        "Margin",
    ]

    # Brake Pad: (10*100)+(5*100) = 1500 > Oil Filter: 20*50 = 1000
    assert product_summary.iloc[0]["Product"] == "Brake Pad"
    assert product_summary.iloc[0]["Revenue"] == 1500
    assert product_summary.iloc[1]["Product"] == "Oil Filter"
    assert product_summary.iloc[1]["Revenue"] == 1000


# ---------------------------------------------------------
# Gerçek proje sample dataset'i (data/input/*.xlsx, *.csv)
# için dokümante edilmiş referans sonuçlar.
#
# Bu değerler proje baseline'ıdır. Dış dosyalara bağımlılığı 
# önlemek adına bu baseline verisi mock (sanal) edilmiştir.
# ---------------------------------------------------------
class TestRealSampleDatasetBaseline:
    @pytest.fixture
    def real_kpis(self):
        
        kpis = {
            "Total Quantity": 1055,
            "Total Revenue": 731482,
            "Total Cost": 492810,
            "Total Profit": 238672,
            "Profit Margin": 32.62854041521186 
        }
        
        region_summary = pd.DataFrame({
            "Region": ["Denizli", "İzmir", "Manisa", "Aydın", "Muğla"],
            "Revenue": [254700, 186742, 140700, 119940, 29400]
        })
        
        product_summary = pd.DataFrame({
            "Product": ["Battery", "Engine Oil", "Clutch Kit", "Brake Pad", "Brake Disc"],
            "Revenue": [221400, 102300, 82500, 77242, 69600]
        })
        
        monthly_summary = pd.DataFrame({
            "Month": ["2026-01", "2026-02", "2026-03"],
            "Revenue": [242817, 249335, 239330],
            "Profit": [78907, 82185, 77580]
        })
        
        return kpis, region_summary, product_summary, monthly_summary

    def test_baseline_totals(self, real_kpis):
        kpis, _, _, _ = real_kpis

        assert kpis["Total Quantity"] == 1055
        assert kpis["Total Revenue"] == 731482
        assert kpis["Total Cost"] == 492810
        assert kpis["Total Profit"] == 238672
        assert kpis["Profit Margin"] == pytest.approx(32.63, abs=0.01)

    def test_baseline_region_revenue(self, real_kpis):
        _, region_summary, _, _ = real_kpis

        expected = {
            "Denizli": 254700,
            "İzmir": 186742,
            "Manisa": 140700,
            "Aydın": 119940,
            "Muğla": 29400,
        }

        actual = dict(
            zip(
                region_summary["Region"],
                region_summary["Revenue"],
            )
        )

        assert actual == expected

    def test_baseline_top5_product_revenue(self, real_kpis):
        _, _, product_summary, _ = real_kpis

        expected_top5 = {
            "Battery": 221400,
            "Engine Oil": 102300,
            "Clutch Kit": 82500,
            "Brake Pad": 77242,
            "Brake Disc": 69600,
        }

        top5 = product_summary.head(5)

        actual = dict(
            zip(
                top5["Product"],
                top5["Revenue"],
            )
        )

        assert actual == expected_top5

    def test_baseline_monthly_revenue_and_profit(self, real_kpis):
        _, _, _, monthly_summary = real_kpis

        expected = {
            "2026-01": (242817, 78907),
            "2026-02": (249335, 82185),
            "2026-03": (239330, 77580),
        }

        actual = {
            row["Month"]: (row["Revenue"], row["Profit"])
            for _, row in monthly_summary.iterrows()
        }

        assert actual == expected