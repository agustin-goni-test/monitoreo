from .output_writer import OutputWriter
from typing import List, Tuple
from polling.poller import PollingStats

class ScreenWriter(OutputWriter):
    def write_default(self, service_name: str, data_matrix: list[list], **kwargs):
        print("Writing to the screen...")
        print(f"Service Name: {service_name}")
        
        header = data_matrix[0]
        for row in data_matrix[1:]:  # Skip header row since we’re labeling columns
            output_row = []
            for col_name, value in zip(header, row):
                # if col_name.lower() != "timestamp" and isinstance(value, (int, float)):
                #     # Add 'seconds' for time values — you could refine this further based on your metric name/type logic
                #     value_str = f"{value} seconds" if "time" in col_name.lower() else str(value)
                # else:
                #     value_str = str(value)
                value_str = str(value)
                output_row.append(f"{col_name}: {value_str}")
            print(", ".join(output_row))
        
        print(f"\nWrote a total of {len(data_matrix) - 1}  data points, with {len(data_matrix[0]) - 1} columns, to the screen")

    
    def write_last_trx_poll(self, polling_data):
        """Output the data in a single screen line"""
        last_trx = polling_data.last_transaction_time
        polling_time = polling_data.current_time
        lag = polling_data.time_lag
        print(f"Polling time: {polling_time} -- Last recorded transaction: {last_trx} -- Time difference {lag:.2f} minutes")

    def finalize_last_trx_poll_file(self):
        print("Output to screen has ended.")

    def write_polling_stats(self, service_name, stats_list: List[Tuple[str, PollingStats]]):
        print(f"\n Inside the screen writer, processing service {service_name} \n")
        for metric_name, stats in stats_list:
            print(f"Metric name: {metric_name}")
            print(f"Mean: {stats.mean:.2f} " 
                  f"- Median: {stats.median:.2f} " 
                  f"- Min: {stats.min:.2f} " 
                  f" - Max: {stats.max:.2f} " 
                  f"- StdDev: {stats.std_dev:.2f} " 
                  f" - Compliance: {stats.compliance}"
                  )


        