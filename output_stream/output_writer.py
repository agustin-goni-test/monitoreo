from abc import ABC, abstractmethod

class OutputWriter(ABC):
    @abstractmethod
    def write_default(self, service_name: str, data_matrix: list[list]):
        pass
