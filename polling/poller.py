from typing import List, Dict
from dataclasses import dataclass
from config_loader import get_config
from dynatrace_client import get_dynatrace_client
from clients.private_site import get_private_site_client
from clients.login import get_login_client
from debugger import Debugger
from typing import List, Tuple, Optional
import statistics
from datetime import datetime
from dotenv import load_dotenv
import os


load_dotenv()


@dataclass
class PollingMetric:
    service_name: str
    service_id: str
    metric_name: str
    metric_id: str
    is_calculated: bool


@dataclass
class PollingStats:
    mean: float
    median: float
    min: float
    max: float
    std_dev: float
    compliance: bool

@dataclass
class TransactionPolling:
    current_time: datetime
    last_transaction_time: datetime
    time_lag: float


class Poller:
    def __init__(self):
        self.config = get_config()
        self.metrics = self._discover_time_metrics()
        self.client = get_dynatrace_client()

    def _is_time_metric(self, metric_name: str) -> bool:
        """Check if the name implies it's a time related metric"""
        return "time" in metric_name.lower() and "timestamp" not in metric_name.lower()
    
    def _discover_time_metrics(self) -> List[PollingMetric]:
        
        metrics = []
        for service in self.config.services:
            # Check builtin metrics:
            for name, id in service.metrics.items():
                # Check if the metric is time based
                if self._is_time_metric(name):
                    # if it is, append to list
                    metrics.append(PollingMetric(
                        service_name = service.name,
                        service_id = service.id,
                        metric_name = name,
                        metric_id = id,
                        is_calculated = False
                    ))

            # Check calculated metrics
            if hasattr(service, 'calculated_metrics') and service.calculated_metrics:
                for name, id in service.calculated_metrics.items():
                    # Check if the metric is time based
                    if self._is_time_metric(name):
                        # If it is, append to list
                        metrics.append(PollingMetric(
                            service_name = service.name,
                            service_id = service.id,
                            metric_name = name,
                            metric_id = id,
                            is_calculated = True
                        ))
        
        return metrics
    
    def poll_metric_from_service(self, metric: PollingMetric) -> PollingStats:
        """
        Get data for a given service and metric (call wrapper).

        Args:
            metric: Information about the metric to poll (includes service).

        Returns:
            Polling stats for the metric.
        """
        client = get_dynatrace_client()
        service_name = metric.service_name
        service_id = metric.service_id
        metric_id = metric.metric_id
        resolution = self.config.polling.resolution
        from_time = self.config.polling.from_time
        to_time = self.config.polling.to_time
        data_matrix = self.client.get_service_metrics(service_id, service_name, metric_id, resolution, from_time, to_time)
        
        # stats = PollingStats()
        # average = self.average_time_ms(data_matrix) / 1000
        return self.calculate_polling_stats(data_matrix)

      


    def average_time_ms(self, metric_data: List[Tuple[int, Optional[float]]]) -> float:
        """
        Calculate average time in milliseconds from raw metric data.
        
        Args:
            metric_data: List of tuples (timestamp, value_in_microseconds)
            
        Returns:
            Average time in milliseconds (float)
            
        Raises:
            ValueError: If no valid data points exist
        """
        valid_values = []
        
        for timestamp, value in metric_data:
            # Skip None values and negative values (invalid data)
            if value is not None and value >= 0:
                # Convert microseconds to milliseconds
                valid_values.append(value / 1000)
        
        if not valid_values:
            raise ValueError("No valid data points to calculate average")
        
        return statistics.mean(valid_values)
    

    def calculate_polling_stats(self, metric_data: List[Tuple[int, Optional[float]]]) -> 'PollingStats':
        """
        Calculate polling statistics from raw metric data.

        Args:
            metric_data: List of tuples (timestamp, value_in_microseconds)

        Returns:
            PollingStats: Aggregated statistics
        """
        valid_values = []

        for timestamp, value in metric_data:
            if value is not None and value >= 0:
                valid_values.append(value / 1000)  # microseconds to milliseconds

        if not valid_values:
            raise ValueError("No valid data points to calculate statistics")

        mean_value = statistics.mean(valid_values)
        median_value = statistics.median(valid_values)
        min_value = min(valid_values)
        max_value = max(valid_values)
        std_dev = statistics.stdev(valid_values) if len(valid_values) > 1 else 0.0

        # To be taken from configuration
        below_threshold_flag = mean_value < 3000

        return PollingStats(
            mean=mean_value / 1000,          # convert to seconds, like you did before
            median=median_value / 1000,      # same conversion
            min=min_value / 1000,
            max=max_value / 1000,
            std_dev=std_dev,
            compliance=below_threshold_flag
        )



    def get_polling_config(self) -> Dict:
        return { 
            "resolution": self.config.polling.resolution,
            "from_time": self.config.polling.from_time,
            "to_time": self.config.polling.to_time
        }
    

    def poll_last_transaction(self) -> TransactionPolling:
        
        # Get client and token
        site_client = get_private_site_client()

        # Get login client to obtain token
        login_client = get_login_client()

        # Authenticate in login service (obtain token)
        token = login_client.authenticate()

        # Set token for private site client
        site_client.set_token(token)
        
        # Find current time
        current_time = datetime.now()

        # Call API
        response = site_client.get_last_transaction()

        # Parse the transaction time
        trx_time_str = response['data']['trx_last']
        last_transaction_time = datetime.strptime(
            trx_time_str, 
            '%Y-%m-%d %H:%M:%S.%f'
        )

        # Calculate the time difference
        time_lag = (current_time - last_transaction_time).total_seconds() / 60

        return TransactionPolling(
            current_time=current_time,
            last_transaction_time=last_transaction_time,
            time_lag=time_lag
        )

    
    def echo_configuration(self):
        """Print the configuration in the debugger"""
        Debugger.echo_polling_metrics(
            self.get_polling_config(),
            self.metrics
        )

            

                    
                
