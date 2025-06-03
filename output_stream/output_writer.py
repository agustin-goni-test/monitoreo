from abc import ABC, abstractmethod
from polling.poller import TransactionPolling, PollingStats
from typing import List, Tuple

class OutputWriter(ABC):
    @abstractmethod
    def write_default(self, service_name: str, data_matrix: list[list], **kwargs):
        pass

    @abstractmethod
    def write_last_trx_poll(self, polling_data: TransactionPolling):
        pass

    @abstractmethod
    def finalize_last_trx_poll_file(self):
        pass

    @abstractmethod
    def write_polling_stats(self, service_name, stats_list: List[Tuple[str, PollingStats]]):
        pass
