from .output_writer import OutputWriter
import os
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

class ExcelWriter(OutputWriter):
    def write_default(self, service_name: str, data_matrix: list[list], **kwargs):
        sheet_name = kwargs.get('sheet_name', 'Sheet1')
        
        output_dir = "output_files"
        os.makedirs(output_dir, exist_ok=True)
        
        base_filename = f"{service_name}_output.xlsx"
        filename = os.path.join(output_dir, base_filename)
        counter = 1
        while os.path.exists(filename):
            filename = os.path.join(output_dir, f"{service_name}_output_{counter}.xlsx")
            counter += 1
        
        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name
        
        # Write header
        header = data_matrix[0]
        ws.append(header)
        
        # Infer column formats once
        col_formats = []
        for col_name in header:
            col_name_lower = col_name.lower()
            if "timestamp" in col_name_lower:
                col_formats.append("text")  # You can refine this if needed
            elif "time" in col_name_lower:
                col_formats.append("time")
            elif "rate" in col_name_lower or "%" in col_name_lower:
                col_formats.append("percentage")
            elif "count" in col_name_lower:
                col_formats.append("integer")
            else:
                col_formats.append("text")
        
        # Write data rows
        for row in data_matrix[1:]:
            output_row = []
            for value, fmt in zip(row, col_formats):
                if value is None:
                    output_row.append("")
                else:
                    try:
                        if fmt == "integer":
                            output_row.append(int(value))
                        elif fmt == "time":
                            output_row.append(float(value))  # Assuming time in seconds
                        elif fmt == "percentage":
                            output_row.append(float(value))  # Assuming decimal form like 0.05 = 5%
                        else:
                            output_row.append(str(value))
                    except (ValueError, TypeError):
                        output_row.append(str(value))
            ws.append(output_row)
        
        # Apply formats
        for col_idx, fmt in enumerate(col_formats, start=1):
            col_letter = ws.cell(row=1, column=col_idx).column_letter
            for cell in ws[col_letter][1:]:  # Skip header
                if fmt == "percentage":
                    cell.number_format = '0.00%'
                elif fmt == "time":
                    cell.number_format = '0.00 "seconds"'
                elif fmt == "integer":
                    cell.number_format = '0'
                # Timestamps and text: leave as is
        
        wb.save(filename)
        
        print(f"\nWrote a total of {len(data_matrix) - 1} data points, with {len(header) - 1} columns, to the Excel file '{filename}' (sheet: '{sheet_name}')")