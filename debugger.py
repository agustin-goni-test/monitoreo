from config_loader import get_config

class Debugger:

    @staticmethod
    def echo_configuration():
        config = get_config()

        print("=== Loaded Configuration ===")
        print("Timeframes:")
        for key, timeframe in config.timeframes.items():
            print(f"  {key}: from={timeframe.from_time}, to={timeframe.to_time}, resolution={timeframe.resolution}")

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

        print("\nDatabases to Monitor:")
        for db in config.databases:
            print(f"  - {db.name} ({db.id})")
            for metric_name, metric_id in db.metrics.items():
                print(f"      * {metric_name}: {metric_id}")

        print("\nOutput Format Configuration:")
        print(f"  Screen: {config.output_format.Screen}")
        print(f"  CSV: {config.output_format.CSV}")
        print(f"  Excel: {config.output_format.Excel}")  # Added Excel as it's in your YAML
        print(f"  All: {config.output_format.All}")
        print(f"  Default: {config.output_format.Default}")
