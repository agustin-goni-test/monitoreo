from .output_writer import OutputWriter
import csv
import os

class CSVWriter(OutputWriter):
    def write_default(self, service_name: str, data_matrix: list[list], **kwargs):
        output_dir = "output_files"  # changed folder name here
        os.makedirs(output_dir, exist_ok=True)  # create folder if missing
        
        base_filename = f"{service_name}_output.csv"
        filename = os.path.join(output_dir, base_filename)
        counter = 1

        while os.path.exists(filename):
            filename = os.path.join(output_dir, f"{service_name}_output_{counter}.csv")
            counter += 1

        with open(filename, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            header = data_matrix[0]
            writer.writerow(header)

            # Write data rows
            for row in data_matrix[1:]:  # Skip header row since we’re labeling columns
                output_row = []
                for col_name, value in zip(header, row):
                    value_str = str(value)
                    output_row.append(value_str)
                writer.writerow(output_row)

        print(f"\nWrote a total of {len(data_matrix) - 1} data points, with {len(data_matrix[0]) - 1} columns, to the CSV file '{filename}'")

