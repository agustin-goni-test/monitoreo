from .output_writer import OutputWriter
from .output_screen import ScreenWriter

class OutputManager:
    def __init__(self):
        self.writer = ScreenWriter()

    def default_output(self, service_name: str, data_matrix: list[list]):
        self.writer.write_default(service_name, data_matrix)
