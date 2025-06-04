from .output_writer import OutputWriter
import csv
import os
from polling.poller import TransactionPolling, PollingStats
from datetime import datetime
from typing import List, Tuple
import glob
import re

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
                    value_str = str(value) if value else ""
                    output_row.append(value_str)
                writer.writerow(output_row)

        print(f"\nWrote a total of {len(data_matrix) - 2} data points, with {len(data_matrix[0]) - 1} columns, to the CSV file '{filename}'")


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
        # filename = os.path.join(output_dir, f"trx_polling_{date_str}.csv")
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

    def write_polling_stats(self, service_name: str, stats_list: List[Tuple[str, PollingStats]]):
        """
        Write polling stats to a CSV file per service.
        Appends to an existing file if it exists (even with timestamp).
        """
        output_dir = "output_files"
        os.makedirs(output_dir, exist_ok=True)

        base_filename = os.path.join(output_dir, f"Poll_{service_name}")
        filename = self._find_existing_file(base_filename)

        file_exists = os.path.exists(filename)
        with open(filename, mode='a', newline='') as csvfile:
            writer = csv.writer(csvfile)

            if not file_exists:
                # Write header row
                header = [
                    "Poll time",
                    "Metric Name",
                    "Mean (ms)",
                    "Median (ms)",
                    "Min (ms)",
                    "Max (ms)",
                    "StdDev (ms)",
                    "Compliance"
                ]
                writer.writerow(header)

            # Write each metric stats
            poll_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for metric_name, stats in stats_list:
                row = [
                    poll_time,
                    metric_name,
                    f"{stats.mean:.2f}",
                    f"{stats.median:.2f}",
                    f"{stats.min:.2f}",
                    f"{stats.max:.2f}",
                    f"{stats.std_dev:.2f}",
                    str(stats.compliance)
                ]
                writer.writerow(row)

        print(f"Appended polling stats to {filename}")


    def finalize_polling_file(self, service_name: str):
        """
        Rename the polling file to include a timestamp (to the second),
        always removing any existing timestamp.
        """
        output_dir = "output_files"
        base_filename = os.path.join(output_dir, f"Poll_{service_name}")
        filename = self._find_existing_file(base_filename)

        if os.path.exists(filename):
            base_name = os.path.splitext(os.path.basename(filename))[0]
            # Remove any existing timestamp suffix
            base_name = re.sub(r' - \d{2}-\d{2}-\d{2}$', '', base_name)
            ext = os.path.splitext(filename)[1]
            timestamp_str = datetime.now().strftime("%H-%M-%S")
            new_filename = f"{base_name} - {timestamp_str}{ext}"
            new_filepath = os.path.join(output_dir, new_filename)
            os.rename(filename, new_filepath)
            print(f"Renamed file to: {new_filepath}")


    def _find_existing_file(self, base_filename: str) -> str:
        """
        Find an existing file matching the base filename (with or without timestamp)
        inside the given output_dir.
        Returns the first matching file or the default base filename path.
        """
        # We expect base_filename to be like 'output_files/Poll_AbonosController'
        pattern = f"{base_filename}*.csv"  # e.g. 'output_files/Poll_AbonosController*.csv'
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
        else:
            return f"{base_filename}.csv"



