from .output_writer import OutputWriter
from .output_screen import ScreenWriter
from .output_excel import ExcelWriter
from .output_csv import CSVWriter  # Add any other writers as needed
from config_loader import get_config
from polling.poller import TransactionPolling

class OutputManager:
    def __init__(self):
        config = get_config()
        self.writers: list[OutputWriter] = []

        available_writers = {
            "Screen": ScreenWriter,
            "CSV": CSVWriter,
            "Excel": ExcelWriter
            # add other writers here later (e.g., JSONWriter)
        }

        selected_writers = []

        # 1. Check if All is True
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

    def default_output(self, service_name: str, data_matrix: list[list]):
        for writer in self.writers:
            if isinstance(writer, ExcelWriter):
                sheet_name = "Default"  # or generate it dynamically if needed
                writer.write_default(service_name, data_matrix, sheet_name=sheet_name)
            else:
                writer.write_default(service_name, data_matrix)
            
    def last_trx_poll_output(self, polling_data: TransactionPolling):
        """Generic implementation for all writers"""
        for writer in self.writers:
            writer.write_last_trx_poll(polling_data)

    def metric_validation_output(self, average, threshold):
        # Check if response is below threshold
        pass

