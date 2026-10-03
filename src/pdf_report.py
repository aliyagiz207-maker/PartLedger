import sys
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

HEADER_COLOR = colors.HexColor("#1F4E78")
SECTION_ROW_COLOR = colors.HexColor("#EAF2F8")

FONT_REGULAR = "DejaVuSans"
FONT_BOLD = "DejaVuSans-Bold"

_FONTS_REGISTERED = False


def get_application_root():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent.parent


def get_resource_root():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)

    return get_application_root()


def register_fonts():
    global _FONTS_REGISTERED

    if _FONTS_REGISTERED:
        return

    resource_root = get_resource_root()
    fonts_folder = resource_root / "assets" / "fonts"

    pdfmetrics.registerFont(
        TTFont(FONT_REGULAR, str(fonts_folder / "DejaVuSans.ttf"))
    )

    pdfmetrics.registerFont(
        TTFont(FONT_BOLD, str(fonts_folder / "DejaVuSans-Bold.ttf"))
    )

    _FONTS_REGISTERED = True


def build_styles():
    base_styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleTR",
        parent=base_styles["Title"],
        fontName=FONT_BOLD,
        fontSize=18,
        spaceAfter=4,
        spaceBefore=0,
    )

    heading2_style = ParagraphStyle(
        "Heading2TR",
        parent=base_styles["Heading2"],
        fontName=FONT_BOLD,
        fontSize=13,
        spaceAfter=6,
        spaceBefore=0,
    )

    heading3_style = ParagraphStyle(
        "Heading3TR",
        parent=base_styles["Heading3"],
        fontName=FONT_BOLD,
        fontSize=11,
        spaceAfter=3,
        spaceBefore=0,
    )

    normal_style = ParagraphStyle(
        "NormalTR",
        parent=base_styles["Normal"],
        fontName=FONT_REGULAR,
    )

    italic_style = ParagraphStyle(
        "ItalicTR",
        parent=base_styles["Italic"],
        fontName=FONT_REGULAR,
    )

    return {
        "Title": title_style,
        "Heading2": heading2_style,
        "Heading3": heading3_style,
        "Normal": normal_style,
        "Italic": italic_style,
    }


KPI_LABELS_TR = {
    "Total Quantity": "Toplam Adet",
    "Total Revenue": "Toplam Ciro",
    "Total Cost": "Toplam Maliyet",
    "Total Profit": "Toplam Kâr",
    "Profit Margin": "Kâr Marjı",
}


def format_currency(value, config):
    return f'{config["currency"]}{value:,.0f}'


def format_percent(value):
    return f"{value:.2f}%"


def build_kpi_table(kpis, config):
    table_data = [["Gösterge", "Değer"]]

    for key, value in kpis.items():
        if "Margin" in key:
            display = format_percent(value)
        elif "Quantity" in key:
            display = f"{value:,.0f}"
        else:
            display = format_currency(value, config)

        table_data.append([KPI_LABELS_TR.get(key, key), display])

    table = Table(table_data, colWidths=[8*cm, 6*cm])

    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
                ("FONTNAME", (0, 1), (-1, -1), FONT_REGULAR),
                ("BACKGROUND", (0, 0), (-1, 0), HEADER_COLOR),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
                ("TOPPADDING", (0, 0), (-1, 0), 4),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 3),
                ("TOPPADDING", (0, 1), (-1, -1), 3),
            ]
        )
    )

    return table


def build_analysis_table(
    dataframe,
    name_column,
    config,
    column_widths,
    display_label=None,
):
    if display_label is None:
        display_label = name_column

    table_data = [[display_label, "Ciro", "Kâr", "Marj"]]

    for _, row in dataframe.iterrows():
        table_data.append(
            [
                str(row[name_column]),
                format_currency(row["Revenue"], config),
                format_currency(row["Profit"], config),
                format_percent(row["Margin"]),
            ]
        )

    table = Table(table_data, colWidths=column_widths)

    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
                ("FONTNAME", (0, 1), (-1, -1), FONT_REGULAR),
                ("BACKGROUND", (0, 0), (-1, 0), HEADER_COLOR),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, SECTION_ROW_COLOR],
                ),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 3),
                ("TOPPADDING", (0, 0), (-1, 0), 3),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 2),
                ("TOPPADDING", (0, 1), (-1, -1), 2),
            ]
        )
    )

    return table


def generate_pdf_report(
    kpis,
    region_summary,
    product_summary,
    monthly_summary,
    config,
):
    register_fonts()
    styles = build_styles()

    application_root = get_application_root()
    resource_root = get_resource_root()

    output_folder = application_root / "data" / "output"
    output_folder.mkdir(parents=True, exist_ok=True)

    # PDF DOSYA İSMİ DÜZELTİLDİ
    output_file = output_folder / "PartLedger_Rapor.pdf"

    document = SimpleDocTemplate(
        str(output_file),
        pagesize=A4,
        topMargin=1.0*cm,
        bottomMargin=1.0*cm,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm,
    )

    elements = []

    logo_file = resource_root / config["logo_path"]

    if logo_file.exists():
        logo = Image(str(logo_file), width=3.5*cm, height=1.75*cm)
        logo.hAlign = "RIGHT"
        elements.append(logo)

    elements.append(
        Paragraph(config["company_name"], styles["Title"])
    )

    elements.append(
        Paragraph(config["dashboard_title"], styles["Heading2"])
    )

    elements.append(Spacer(1, 4))

    elements.append(
        Paragraph("Temel Performans Göstergeleri", styles["Heading3"])
    )
    elements.append(Spacer(1, 4))
    elements.append(build_kpi_table(kpis, config))
    elements.append(Spacer(1, 8))

    if not region_summary.empty:
        elements.append(
            KeepTogether(
                [
                    Paragraph(
                        "Bölgesel Performans", styles["Heading3"]
                    ),
                    Spacer(1, 4),
                    build_analysis_table(
                        region_summary,
                        "Region",
                        config,
                        column_widths=[5*cm, 4*cm, 4*cm, 3*cm],
                        display_label="Bölge",
                    ),
                ]
            )
        )
        elements.append(Spacer(1, 8))

    if not product_summary.empty:
        top5 = (
            product_summary
            .sort_values("Revenue", ascending=False)
            .head(5)
        )

        elements.append(
            KeepTogether(
                [
                    Paragraph(
                        "En Çok Satan 5 Ürün", styles["Heading3"]
                    ),
                    Spacer(1, 4),
                    build_analysis_table(
                        top5,
                        "Product",
                        config,
                        column_widths=[5*cm, 4*cm, 4*cm, 3*cm],
                        display_label="Ürün",
                    ),
                ]
            )
        )
        elements.append(Spacer(1, 8))

    if not monthly_summary.empty:
        elements.append(
            KeepTogether(
                [
                    Paragraph(
                        "Aylık Performans", styles["Heading3"]
                    ),
                    Spacer(1, 4),
                    build_analysis_table(
                        monthly_summary,
                        "Month",
                        config,
                        column_widths=[5*cm, 4*cm, 4*cm, 3*cm],
                        display_label="Ay",
                    ),
                ]
            )
        )
        elements.append(Spacer(1, 8))

    elements.append(
        Paragraph(
            f"Oluşturulma: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            styles["Normal"],
        )
    )

    elements.append(Spacer(1, 4))

    elements.append(
        Paragraph("PartLedger tarafından oluşturuldu", styles["Italic"])
    )

    document.build(elements)