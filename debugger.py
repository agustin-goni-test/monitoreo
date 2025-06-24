from config_loader import get_config
from clients.synth_monitor import get_synth_monitor_client
from typing import Dict, List

class Debugger:

    @staticmethod
    def echo_configuration():
        config = get_config()

        print("=== Loaded Configuration ===")
        
        # Timeframes
        print("Timeframes:")
        for key, timeframe in config.timeframes.items():
            print(f"  {key}: from={timeframe.from_time}, to={timeframe.to_time}, resolution={timeframe.resolution}")

        # Services
        print("\nServices to Monitor:")
        for service in config.services:
            print(f"  - {service.name} ({service.id}) with threshold {service.threshold_ms}ms")
            print("    Metrics:")
            for metric_name, metric_id in service.metrics.items():
                print(f"      * {metric_name}: {metric_id}")
            
            # Corrected spelling and added check for non-empty dict
            if hasattr(service, 'calculated_metrics') and service.calculated_metrics:
                print("    Calculated Metrics:")
                for calc_name, calc_id in service.calculated_metrics.items():
                    print(f"      * {calc_name}: {calc_id}")

        # Databases
        print("\nDatabases to Monitor:")
        for db in config.databases:
            print(f"  - {db.name} ({db.id})")
            for metric_name, metric_id in db.metrics.items():
                print(f"      * {metric_name}: {metric_id}")

        # Output formats
        print("\nOutput Format Configuration:")
        print(f"  Screen: {config.output_format.Screen}")
        print(f"  CSV: {config.output_format.CSV}")
        print(f"  Excel: {config.output_format.Excel}")  # Added Excel as it's in your YAML
        print(f"  All: {config.output_format.All}")
        print(f"  Default: {config.output_format.Default}")

        # Polling 
        print("\nPolling Configuration:")
        print(f"  Resolution: {config.polling.resolution}")
        print(f"  From Time: {config.polling.from_time}")
        print(f"  To Time: {config.polling.to_time}")

        # Flow Control
        print("\nFlow Control Configuration:")

        # Services Flow Control
        print("  Services:")
        print(f"    Query Enabled: {config.flow_control.services.query_enabled}")
        print(f"    Include Calculated Metrics: {config.flow_control.services.include_calculated_metrics}")
        print("    Timeframes:")
        for timeframe_name, enabled in config.flow_control.services.timeframes.__dict__.items():
            print(f"      * {timeframe_name}: {enabled}")

        # Databases Flow Control
        print("  Databases:")
        print(f"    Query Enabled: {config.flow_control.databases.query_enabled}")

        # Polling Flow Control
        print("  Polling:")
        print(f"    Last Transaction Polling: {config.flow_control.polling.last_trx_polling}")
        print(f"    Service Polling: {config.flow_control.polling.service_polling}")
        print(f"    Monitor Update Polling: {config.flow_control.polling.monitor_update_polling}")

    @staticmethod
    def echo_polling_metrics(polling_config: Dict, metrics: List['PollingMetric']):
        """Print polling configuration and metrics"""
        print("\n=== Polling Configuration ===")
        print(f"Resolution: {polling_config['resolution']}")
        print(f"Time Range: {polling_config['from_time']} to {polling_config['to_time']}")
        
        print("\n=== Metrics Being Polled ===")
        for metric in metrics:
            metric_type = "Calculated" if metric.is_calculated else "Builtin"
            print(f"{metric.service_name} ({metric.service_id}):")
            print(f"  - {metric.metric_name} ({metric_type})")
            print(f"    ID: {metric.metric_id}")

    @staticmethod
    def echo_synth_monitor_client_config():
        synthetic_monitor_client = get_synth_monitor_client()
        print("\n=== Synthetic monitor client configuration")
        print(f"Environment URL v1: {synthetic_monitor_client.environment_url_v1}")
        print(f"Environment URL v2: {synthetic_monitor_client.environment_url_v2}")
        print(f"Configuration URL: {synthetic_monitor_client.configuration_url}")
        print(f"User token: {synthetic_monitor_client.user_token}")
        print(f"Monitor admin token: {synthetic_monitor_client.monitor_admin_token}")



