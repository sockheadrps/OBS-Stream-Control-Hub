from reportlab.lib.pagesizes import portrait, letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from ..data.charts.generator_data import get_generator_data
from ..config import image_dir

# load the fuel_bar.png
fuel_bar = Image(str(image_dir / "fuel_bar.png"), width=544, height=400)


def generate_pdf(data, filename="table_report.pdf"):
    """
    Generates a PDF from the provided table data with enhanced styling.

    Args:
        data (dict): Dictionary with table rows, columns, and other metadata.
        filename (str): The name of the PDF file to save.
    """
    # Extract table data
    headers = ["Name", "Fuel Input (%)", "Estimated Current Fuel (gal)", "Fuel Delta"]
    sorted_generators = reversed(sorted(data, key=lambda gen: (
    gen.fuelInput / 100) * gen.capacity))
    rows = [
        [
            gen.name,
            gen.fuelInput,
            round(gen.fuelInput / 100 * gen.capacity),
            gen.capacity - (round(gen.fuelInput / 100 * gen.capacity))
        ]
        for gen in sorted_generators
    ]

    # Add totals row
    total_fuel = sum(row[3] for row in rows)
    rows.append(["Total", "", "", total_fuel])

    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    title_style.alignment = 1  # Center alignment
    table_header_style = ParagraphStyle(
        "TableHeader",
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=colors.whitesmoke,
        alignment=1,  # Center alignment
        spaceBefore=6,
        spaceAfter=6,
    )
    cell_style = ParagraphStyle(
        "TableCell",
        fontName="Helvetica",
        fontSize=9,
        alignment=1,  # Center alignment
        spaceBefore=4,
        spaceAfter=4,
    )

    # Create a PDF document
    pdf = SimpleDocTemplate(
        filename,
        pagesize=portrait(letter),
        leftMargin=36,  # 0.5 inch margins
        rightMargin=36,
        topMargin=15,   # 1 inch top margin
        bottomMargin=10 # 1 inch bottom margin
    )

    # Combine headers and rows
    table_data = [headers] + rows

    # Calculate available width and column proportions
    available_width = letter[0] - 72  # Total width minus margins
    col_widths = [
        available_width * 0.25,  # Name - 25%
        available_width * 0.2,   # Fuel Input - 20%
        available_width * 0.3,   # Est Current Fuel - 30%
        available_width * 0.25   # Fuel Delta - 25%
    ]

    # Style the table
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F9FAFB")),
        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#D1D5DB")),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#374151")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F3F4F6")]),
    ]))

    # Build PDF with table and fuel bar chart
    elements = [table, Spacer(1, 15), fuel_bar]
    pdf.build(elements)

# Example usage
if __name__ == "__main__":
    gen_data = get_generator_data()
    generate_pdf(gen_data)
