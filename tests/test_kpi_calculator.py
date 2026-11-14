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
    kpis, _, _, _, _ = calculate_kpis(df)
    assert kpis["Total Quantity"] == 35


def test_total_revenue():
    df = build_sample_df()
    kpis, _, _, _, _ = calculate_kpis(df)
    # (10*100) + (5*100) + (20*50) = 1000 + 500 + 1000
    assert kpis["Total Revenue"] == 2500


def test_total_cost():
    df = build_sample_df()
    kpis, _, _, _, _ = calculate_kpis(df)
    # (10*60) + (5*60) + (20*30) = 600 + 300 + 600
    assert kpis["Total Cost"] == 1500


def test_total_profit():
    df = build_sample_df()
    kpis, _, _, _, _ = calculate_kpis(df)
    assert kpis["Total Profit"] == 1000


def test_profit_margin():
    df = build_sample_df()
    kpis, _, _, _, _ = calculate_kpis(df)
    # 1000 / 2500 * 100 = 40.0
    assert kpis["Profit Margin"] == pytest.approx(40.0)


def test_enriched_dataframe_contains_calculated_columns():
    df = build_sample_df()
    _, _, _, _, enriched_df = calculate_kpis(df)

    assert "Revenue" in enriched_df.columns
    assert "Cost" in enriched_df.columns
    assert "Profit" in enriched_df.columns
    assert list(enriched_df["Revenue"]) == [1000, 500, 1000]
    assert list(enriched_df["Profit"]) == [400, 200, 400]


def test_profit_margin_zero_revenue_does_not_crash():
    df = pd.DataFrame({
        "Date": ["2026-01-01"],
        "Product": ["Brake Pad"],
        "Region": ["İzmir"],
        "Quantity": [0],
        "UnitPrice": [100],
        "UnitCost": [60],
    })

    kpis, _, _, _, _ = calculate_kpis(df)

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

    kpis, region_summary, product_summary, monthly_summary, enriched_df = calculate_kpis(df)

    assert kpis["Total Quantity"] == 0
    assert kpis["Total Revenue"] == 0
    assert kpis["Profit Margin"] == 0
    assert region_summary.empty
    assert product_summary.empty
    assert monthly_summary.empty
    assert enriched_df.empty


def test_region_summary_columns_and_sort_order():
    df = build_sample_df()
    _, region_summary, _, _, _ = calculate_kpis(df)

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
    _, _, product_summary, _, _ = calculate_kpis(df)

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


class TestMultiMonthDatasetCalculation:
    @pytest.fixture
    def calculated_outputs(self):
        sample_df = pd.DataFrame({
            "Date": [
                "2026-01-10",
                "2026-01-20",
                "2026-02-05",
                "2026-02-18",
                "2026-03-12",
            ],
            "Product": [
                "Battery",
                "Engine Oil",
                "Clutch Kit",
                "Brake Pad",
                "Brake Disc",
            ],
            "Region": [
                "Denizli",
                "İzmir",
                "Manisa",
                "Aydın",
                "Muğla",
            ],
            "Quantity": [20, 50, 30, 40, 10],
            "UnitPrice": [4100.0, 620.0, 2750.0, 893.0, 1450.0],
            "UnitCost": [3300.0, 410.0, 1850.0, 540.0, 980.0],
        })
        return calculate_kpis(sample_df)

    def test_multi_month_totals(self, calculated_outputs):
        kpis, _, _, _, _ = calculated_outputs

        assert kpis["Total Quantity"] == 150
        assert kpis["Total Revenue"] == 245720.0
        assert kpis["Total Cost"] == 173400.0
        assert kpis["Total Profit"] == 72320.0
        assert kpis["Profit Margin"] == pytest.approx(29.431873677, abs=0.01)

    def test_multi_month_region_ordering(self, calculated_outputs):
        _, region_summary, _, _, _ = calculated_outputs

        expected = {
            "Manisa": 82500.0,
            "Denizli": 82000.0,
            "Aydın": 35720.0,
            "İzmir": 31000.0,
            "Muğla": 14500.0,
        }
        actual = dict(zip(region_summary["Region"], region_summary["Revenue"]))
        assert actual == expected

    def test_multi_month_summary_breakdown(self, calculated_outputs):
        _, _, _, monthly_summary, _ = calculated_outputs

        expected = {
            "2026-01": (113000.0, 26500.0),
            "2026-02": (118220.0, 41120.0),
            "2026-03": (14500.0, 4700.0),
        }
        actual = {
            row["Month"]: (row["Revenue"], row["Profit"])
            for _, row in monthly_summary.iterrows()
        }
        assert actual == expected