from abc import ABC, abstractmethod
from polling.poller import TransactionPolling

class OutputWriter(ABC):
    @abstractmethod
    def write_default(self, service_name: str, data_matrix: list[list], **kwargs):
        pass

    @abstractmethod
    def write_last_trx_poll(self, polling_data: TransactionPolling):
        pass
