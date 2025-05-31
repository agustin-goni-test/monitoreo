from .output_writer import OutputWriter
from .output_screen import ScreenWriter
from .output_csv import CSVWriter  # Add any other writers as needed
from config_loader import get_config

class OutputManager:
    def __init__(self):
        config = get_config()
        self.writers: list[OutputWriter] = []

        available_writers = {
            "Screen": ScreenWriter,
            "CSV": CSVWriter,
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
            writer.write_default(service_name, data_matrix)

