import csv
import zipfile
from ..db.db_manager import DatabaseManager
from pathlib import Path
import pandas as pd

# Define base directory and report directory
base_dir = Path(__file__).parent.parent
report_dir = base_dir / "data" / "reports"

# Ensure the report directory exists
report_dir.mkdir(parents=True, exist_ok=True)


def generate_csv(month: str, report_type: str):
    # Gather data from the database
    all_gen_data, columns, gen_names = gather_gen_data(month, report_type)

    # Define CSV fieldnames
    fieldnames = ["gen_name"]
    fieldnames.extend(columns)

    # create the folder for the month if it doesn't exist
    month_dir = report_dir / month
    month_dir.mkdir(parents=True, exist_ok=True)

    # CSV file path
    csv_file_path = month_dir / f"{report_type}.csv"

    # Write data to the CSV file
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for item in all_gen_data:
            for gen_name, gen_data in item.items():
                # Extract entries for the specified report type ('pre' or 'post')
                if report_type in gen_data:
                    for entry in gen_data[report_type]["entries"]:
                        row = {"gen_name": gen_name}
                        row.update(
                            {col: val for col, val in zip(columns, entry)})
                        if "leaks" in row:
                            row["leaks"] = "Yes" if row["leaks"] == 1 else "No"
                        if "oil_check" in row:
                            row["oil_check"] = "acceptable" if row["oil_check"] == 1 else "unacceptable"
                        if "run_hours" in row:
                            row["run_hours"] = str(row["run_hours"])
                        writer.writerow(row)
    return csv_file_path


def gather_gen_data(month: str, report_type: str):
    # Instantiate the DatabaseManager and gather generator data
    db_manager = DatabaseManager()
    all_gen_data = []
    columns = db_manager.pre_columns if report_type == "pre" else db_manager.post_columns
    for gen in db_manager.gen_names:
        # Get entries with just month and generator name
        gen_data = db_manager.get_entries(month, gen)
        all_gen_data.append({gen: gen_data})
    return (all_gen_data, columns, db_manager.gen_names)


def generate_csv_reports(month: str):
    # Generate reports for "pre" and "post" data
    pre_csv = generate_csv(month, "pre")
    post_csv = generate_csv(month, "post")
    return {"pre": pre_csv, "post": post_csv}


def generate_excel_reports(month: str):
    """Generate formatted reports and create a zip file containing them."""
    month_dir = report_dir / month
    month_dir.mkdir(parents=True, exist_ok=True)

    # Generate CSV and Excel reports
    generate_csv_reports(month)

    convert_to_excel(month)

    # Create combined report
    combined_excel = month_dir / f"{month}_report.xlsx"
    pre_df = pd.read_csv(month_dir / "pre.csv")
    post_df = pd.read_csv(month_dir / "post.csv")
    clean_up_csv_files(month)


    with pd.ExcelWriter(combined_excel, engine='xlsxwriter') as writer:
        # Write sheets
        pre_df.to_excel(writer, index=False, sheet_name='Pre Run')
        post_df.to_excel(writer, index=False, sheet_name='Post Run')
        
        # Format both sheets
        _format_excel_sheet(writer, pre_df, 'Pre Run')
        _format_excel_sheet(writer, post_df, 'Post Run')
        
    return combined_excel

def convert_to_excel(month: str):
    """Convert CSV reports to Excel files with formatting."""
    month_dir = report_dir / month
    pre_csv = month_dir / "pre.csv"
    post_csv = month_dir / "post.csv"

    # Read CSV files
    pre_df = pd.read_csv(pre_csv)
    post_df = pd.read_csv(post_csv)

    # Create Excel files
    pre_excel = pre_csv.with_suffix(".xlsx")
    post_excel = post_csv.with_suffix(".xlsx")

    # Save individual Excel files
    with pd.ExcelWriter(pre_excel, engine='xlsxwriter') as writer:
        pre_df.to_excel(writer, index=False, sheet_name='Pre Run')
        _format_excel_sheet(writer, pre_df, 'Pre Run')

    with pd.ExcelWriter(post_excel, engine='xlsxwriter') as writer:
        post_df.to_excel(writer, index=False, sheet_name='Post Run')
        _format_excel_sheet(writer, post_df, 'Post Run')

        
def _format_excel_sheet(writer, df, sheet_name):
    """Helper function to format Excel sheets consistently."""
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]

    # Add formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#0066cc', 
        'font_color': 'white',
        'border': 1,
        'text_wrap': True,
        'valign': 'vcenter',
        'align': 'center'
    })

    cell_format = workbook.add_format({
        'border': 1,
        'text_wrap': True,
        'valign': 'top',
        'align': 'center'
    })

    # Set specific column widths based on content type
    column_widths = {
        'gen_name': 10,
        'fuel_level': 12, 
        'battery_vdc': 12,
        'run_hours': 12,
        'coolant_temp': 12,
        'leaks': 8,
        'oil_check': 12,
        'notes': 40,
        'last_updated': 20
    }

    # Write data starting at row 0, col 0 without padding
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
        width = column_widths.get(value, 15)  # Default to 15 if not specified
        worksheet.set_column(col_num, col_num, width, cell_format)

    # Add table with filtering
    worksheet.add_table(0, 0, len(df), len(df.columns) - 1, {
        'style': 'Table Style Medium 2',
        'columns': [{'header': col} for col in df.columns],
        'first_column': True,
        'autofilter': True
    })

    # Write the data, handling NaN values
    for row_num, row_data in enumerate(df.values):
        for col_num, value in enumerate(row_data):
            # Handle NaN/INF values by converting to empty string
            if pd.isna(value) or (isinstance(value, float) and (value == float('inf') or value == float('-inf'))):
                worksheet.write_blank(row_num + 1, col_num, None, cell_format)
            else:
                worksheet.write(row_num + 1, col_num, value, cell_format)

    # Freeze the header row
    worksheet.freeze_panes(1, 0)

def clean_up_csv_files(month: str):
    # delete the csv files
    pre_csv = report_dir / month / "pre.csv"
    post_csv = report_dir / month / "post.csv"
    pre_csv.unlink()
    post_csv.unlink()

def clean_up_excel_files(month: str):
    # delete the excel files
    pre_excel = report_dir / month / "pre.xlsx"
    post_excel = report_dir / month / "post.xlsx"
    combined_excel = report_dir / month / f"{month}_report.xlsx"
    pre_excel.unlink()
    post_excel.unlink()
    combined_excel.unlink()


def generate_zip_reports(month: str):
    """Generate formatted reports and create a zip file containing them."""
    month_dir = report_dir / month
    month_dir.mkdir(parents=True, exist_ok=True)

    # Generate CSV and Excel reports
    generate_csv_reports(month)

    convert_to_excel(month)

    # Create combined report
    combined_excel = month_dir / f"{month}_report.xlsx"
    pre_df = pd.read_csv(month_dir / "pre.csv")
    post_df = pd.read_csv(month_dir / "post.csv")
    clean_up_csv_files(month)


    with pd.ExcelWriter(combined_excel, engine='xlsxwriter') as writer:
        # Write sheets
        pre_df.to_excel(writer, index=False, sheet_name='Pre Run')
        post_df.to_excel(writer, index=False, sheet_name='Post Run')
        
        # Format both sheets
        _format_excel_sheet(writer, pre_df, 'Pre Run')
        _format_excel_sheet(writer, post_df, 'Post Run')

    # Create zip file containing the combined report
    zip_path = month_dir / f"{month.lower()}_reports.zip"
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(combined_excel, combined_excel.name)
    clean_up_excel_files(month)


def get_report_data(month: str, report_type: str):
    # Gather raw data from database
    all_gen_data, columns, gen_names = gather_gen_data(month, report_type)

    report_data = []
    for item in all_gen_data:
        for gen_name, gen_data in item.items():
            if report_type in gen_data:
                for entry in gen_data[report_type]["entries"]:
                    row = {"gen_name": gen_name}
                    row.update({col: val for col, val in zip(columns, entry)})
                    if "leaks" in row:
                        row["leaks"] = "Yes" if row["leaks"] == 1 else "No"
                    if "oil_check" in row:
                        row["oil_check"] = "acceptable" if row["oil_check"] == 1 else "unacceptable" 
                    if "run_hours" in row:
                        row["run_hours"] = str(row["run_hours"])
                    report_data.append(row)
    return report_data if report_data else None
