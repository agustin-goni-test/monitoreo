from .output_writer import OutputWriter
import csv
import os
from polling.poller import TransactionPolling
from datetime import datetime

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


    def write_last_trx_poll(self, polling_data: TransactionPolling):
        """
        Write transaction polling data to a daily CSV file.
        """
        output_dir = "output_files"
        os.makedirs(output_dir, exist_ok=True)

        date_str = datetime.now().strftime("%Y_%m_%d")
        filename = os.path.join(output_dir, f"trx_polling_{date_str}.csv")

        file_exists = os.path.exists(filename)
        with open(filename, mode='a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow([
                    "Poll time",
                    "Last transaction",
                    "Lag (min)"
                ])
            writer.writerow([
                polling_data.current_time.isoformat(),
                polling_data.last_transaction_time.isoformat(),
                f"{polling_data.time_lag:.2f}"
            ])
        print(f"Appended polling data to {filename}")


    def finalize_last_trx_poll_file(self):
        """
        Rename the current day's polling file to include a timestamp when the process is interrupted.
        """
        output_dir = "output_files"
        date_str = datetime.now().strftime("%Y_%m_%d")
        filename = os.path.join(output_dir, f"trx_polling_{date_str}.csv")

        if os.path.exists(filename):
            base, ext = os.path.splitext(filename)
            # Remove any existing timestamp suffix
            if " - " in base:
                base = base.split(" - ")[0]
            timestamp_str = datetime.now().strftime("%H-%M-%S")
            new_filename = f"{base} - {timestamp_str}{ext}"
            os.rename(filename, new_filename)
            print(f"Renamed file to: {new_filename}")


