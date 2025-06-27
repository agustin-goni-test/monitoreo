import pandas as pd
from datetime import datetime
import os

class ExcelEnhancer:
    def __init__(self, file_name):
        self.original_file_name = file_name
        if not file_name.endswith('.xlsx'):
            raise ValueError("File name must end with '.xlsx'.")
        self.enhanced_file_name = None

    def get_output_file_name(self):
        """Generate and set the output file name for the enhanced Excel file inside an 'output' folder."""
        base_name = os.path.basename(self.original_file_name)
        name, ext = os.path.splitext(base_name)
        output_dir = os.path.join(os.path.dirname(self.original_file_name), "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.enhanced_file_name = os.path.join(output_dir, f"{name}_ENH{ext}")


    def set_file_name(self, file_name):
        """Set the file name for the Excel file."""
        if not isinstance(file_name, str):
            raise ValueError("File name must be a string.")
        if not file_name.endswith('.xlsx'):
            raise ValueError("File name must end with '.xlsx'.")
        self.file_name = file_name

    def add_context_columns(self, output_file_name=None):
        """Add context columns to the Excel file."""

        # Load the Excel file
        try:   
            df = pd.read_excel(self.original_file_name)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {self.original_file_name} does not exist.")
        except Exception as e:
            raise Exception(f"An error occurred while reading the file: {str(e)}")
        
        # Check column A is a timestamp column
        timestamp_col = df.columns[0]

        # Convert timestamp column to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
            try:
                df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors='coerce')
            except Exception as e:
                raise ValueError(f"Column {timestamp_col} cannot be converted to datetime: {str(e)}")
            
        # Add context columns
        df.insert(1, "Date", df[timestamp_col].dt.date.astype(str))
        df.insert(2, "Month", df[timestamp_col].dt.month)
        df.insert(3, "Day", df[timestamp_col].dt.day)
        df.insert(4, "Weekday", df[timestamp_col].dt.strftime('%a'))

        if self.enhanced_file_name is None:
            self.get_output_file_name()

        df.to_excel(self.enhanced_file_name, index=False)
        print(f"Enhanced file saved as {self.enhanced_file_name}")

        




        

def main():
    print("Hello from excel_enhancer.py!\n")
    print(os.getcwd())

    # Create ExcelEnhancer instance
    enhancer = ExcelEnhancer("enhancer/ComercioTransaccionesController_CALC.xlsx")

    # Add context columns to the Excel file
    try:
        enhancer.add_context_columns()
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    print("The end")



if __name__ == "__main__":
    main()