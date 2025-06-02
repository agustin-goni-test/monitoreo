from typing import List, Dict
from dataclasses import dataclass
from config_loader import get_config
from debugger import Debugger

@dataclass
class PollingMetric:
    service_name: str
    metric_name: str
    metric_id: str
    is_calculated: bool

class Poller:
    def __init__(self):
        self.config = get_config()
        self.metrics = self._discover_time_metrics()

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
                            metric_name = name,
                            metric_id = id,
                            is_calculated = True
                        ))
        
        return metrics
    
    def get_polling_config(self) -> Dict:
        return { 
            "resolution": self.config.polling.resolution,
            "from_time": self.config.polling.from_time,
            "to_time": self.config.polling.to_time
        }
    
    def echo_configuration(self):
        """Print the configuration in the debugger"""
        Debugger.echo_polling_metrics(
            self.get_polling_config(),
            self.metrics
        )

            

                    
                
