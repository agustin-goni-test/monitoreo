from .output_writer import OutputWriter
from .output_screen import ScreenWriter
from .output_excel import ExcelWriter
from .output_csv import CSVWriter  # Add any other writers as needed
from config_loader import get_config
from polling.poller import TransactionPolling, PollingStats
from typing import List, Tuple

class OutputManager:
    def __init__(self):
        config = get_config()
        self.writers: list[OutputWriter] = []

        # List of available writers (extensible)
        available_writers = {
            "Screen": ScreenWriter,
            "CSV": CSVWriter,
            "Excel": ExcelWriter
            # add other writers here later (e.g., JSONWriter)
        }

        # Structure to hold selected writer (per configuration)
        selected_writers = []

        # 1. Check if All is True. If so, add them all
        if config.output_format.All:
            selected_writers = list(available_writers.keys())
        else:
            # 2. Collect all selected writers
            for writer_name in available_writers.keys():
                if getattr(config.output_format, writer_name):
                    selected_writers.append(writer_name)

            # 3. If none selected, use Default
            if not selected_writers:
                default_writer_name = config.output_format.Default
                if default_writer_name in available_writers:
                    selected_writers = [default_writer_name]
                else:
                    raise ValueError(f"Unknown default output writer: {default_writer_name}")

        # 4. Instantiate selected writers
        for writer_name in selected_writers:
            writer_class = available_writers[writer_name]
            self.writers.append(writer_class())

    def default_output(self, service_name: str, data_matrix: list[list], **kwargs):
        """Creates the output as used with the default configuration"""

        timeframe = kwargs.get('timeframe')
        print(timeframe)
        
        # Iterate through all writers
        for writer in self.writers:
            
            # If one of the select writers is for an Excel output
            if isinstance(writer, ExcelWriter):                
                # Pass sheet name as additional argument
                # sheet_name = "Default"  # or generate it dynamically if needed
                writer.write_default(service_name, data_matrix, sheet_name=timeframe)
            elif isinstance(writer, CSVWriter):
                suffix = timeframe
                writer.write_default(service_name, data_matrix, suffix=timeframe)
           
            else:
                writer.write_default(service_name, data_matrix)
            
    def last_trx_poll_output(self, polling_data: TransactionPolling):
        """Used to generate the output for last transaction polling.   
        Generic implementation for all writers."""
        for writer in self.writers:
            writer.write_last_trx_poll(polling_data)
        
    def service_poll_output(self, service_name, stats_pairs: List[Tuple[str, PollingStats]]):
        """Used for managing the output of service polling.
        Generic implementation for all writers."""
        for writer in self.writers:
            writer.write_polling_stats(service_name, stats_pairs)

    
    def finalize_last_trx_poll_files(self):
        """Used to rename and close the file, when needed (depending
        on writer type)"""
        for writer in self.writers:
            writer.finalize_last_trx_poll_file()

    def finalize_polling_file(self, service_name):
        """Used to rename and close the file, when needed (depending
        on writer type)"""
        for writer in self.writers:
            writer.finalize_polling_file(service_name)

    def metric_validation_output(self, average, threshold):
        # Check if response is below threshold
        pass

