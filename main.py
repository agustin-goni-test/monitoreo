from config_loader import get_config
from debugger import Debugger
from dynatrace_client import get_dynatrace_client
from output_stream.output_manager import OutputManager
from polling.poller import Poller, TransactionPolling, PollingStats
from clients.login import get_login_client
from clients.private_site import get_private_site_client
from dotenv import load_dotenv
import os
from datetime import datetime
import time
from collections import defaultdict
from typing import List, Tuple

_output_manager = OutputManager()
_poller = Poller()

def get_output_manager():
    return _output_manager

def get_poller():
    return _poller

def main():

    load_dotenv()

    # Obtain configuration
    config = get_config()
    
    # Obtain poller
    poller = get_poller()


    if config.debug:
        print(f"Debug mode: {config.debug}")
        Debugger.echo_configuration()
        poller.echo_configuration()



    
    ############### MAIN CONTROL FLOW #########################

    # This is the main condition. Execute if service query is enabled,
    # calculated metrics are included, and timeframe is default
    if (
        config.flow_control.services.query_enabled and 
        config.flow_control.services.include_calculated_metrics and
        config.flow_control.services.timeframes.default
    ):
        get_all_metrics_default_period()

    else:
        # If service query is enabled in control flow
        if config.flow_control.services.query_enabled:
            
            # Get historical metrics. Use timeframes in configuration
            get_historical_service_metrics()

            # If calculated metrics are included
            # They only include the default period
            if config.flow_control.services.include_calculated_metrics:
                get_calculated_service_metrics()
    
    if config.flow_control.databases.query_enabled:
        get_historical_database_metrics()
    
    if config.flow_control.polling.last_trx_polling:
        # Activate last transaction polling
        # Use retries just in case there are timeouts
        error_count = 0       
        retry_polling = True
        
        # Iterate forever to retry until broken by user
        while True:
            retry_polling = start_last_trx_polling()
            if not retry_polling:
                break
            print("Polling has restarted after error...")
            error_count += 1
        
        print(f"Number of errors and restarts: {error_count}")

    elif config.flow_control.polling.service_polling:
        # Service polling, including calculated metrics
        start_service_polling()

    print("THE END")




def get_historical_service_metrics():
    """Main method to get the corresponding service metrics.
    ONLY builtin metrics.
    It takes no arguments. The future implementation will consider
    using flags to determine the periods"""

    # Get the global objects and the configuration
    client = get_dynatrace_client()
    output_manager = get_output_manager()
    config = get_config()

    # This variables are not in use yet. They will be once we have the fixed periods
    # for the queries in place.
    # DEFAULT = True

    # This timeframes are taken from the configuration.
    # The methods to be called are part of the Dynatrace client class.
    timeframes = [
        ("DEFAULT", config.flow_control.services.timeframes.default, "read_all_service_metrics_default"),
        ("YEAR", config.flow_control.services.timeframes.year,  "read_all_service_metrics_year"), 
        ("MONTH", config.flow_control.services.timeframes.month, "read_all_service_metrics_month"),
        ("WEEK", config.flow_control.services.timeframes.week, "read_all_service_metrics_week"),
        ("DAY", config.flow_control.services.timeframes.day, "read_all_service_metrics_day")
    ]
    
    # Iterate through all the services to find the metrics
    for service in config.services:
        print(f"Querying service {service.name}")

        # This flow will execute all the outputs that are indicated in the 
        # configuration. Therefore, this evaluates all conditions one by one,
        # and queries for all active periods.

        for timeframe, is_active, method_name in timeframes:
            if not is_active:
                continue

            # Dynamically get the appropriate client method to call
            client_method = getattr(client, method_name)

            try:
                # Get raw data for the service metrics.
                # Use the dynamic service call
                data_matrix = client_method(service)

                # Add compliance checks for time-related metrics
                complete_matrix = add_time_threshold_columns(data_matrix, service)
                
                # Direct ouput to the selected channels
                # For now we are using the default output...
                output_manager.default_output(service.name, complete_matrix, timeframe=timeframe)

            except Exception as e:
                print(f"Error processing {timeframe} timeframe for {service.name}: {str(e)}")
                continue


def get_calculated_service_metrics():
    """Get the calculated metrics as defined in the configuration.
    This flow is to get those metrics ONLY (no the builtin ones)"""
    
    # Get the global objects and the configuration
    client = get_dynatrace_client()
    output_manager = get_output_manager()
    config = get_config()

    # Iterate through all the services to find the metrics
    for service in config.services:
        print(f"Querying calculated metrics for service {service.name}")

        # Find if the service has calculated metrics included in the configuration
        # Uses helper method for the ServiceMetricConfig class (included in config_loader.py)
        if service.has_calculated_metrics():

            # Get raw data from the calculated metrics
            calc_matrix = client.read_all_calculated_service_metrics_default(service)

            # Add compliance checks for time-related metrics
            calc_complete = add_time_threshold_columns(calc_matrix, service)

            # Direct ouput to the selected channels
            output_manager.default_output(service.name, calc_complete, timeframe="CALC")
        
        else:
            print(f"Service {service.name} has no calculated metrics.")


def get_all_metrics_default_period():
    """Get all the metrics, whether builtin or calculated.
    Keep in mind that calculated metrics only bring data from the moment
    they were created, and hence have no 'history' """
    
    # Get the global objects and the configuration
    client = get_dynatrace_client()
    output_manager = get_output_manager()
    config = get_config()

    # Iterate through all the services to find the metrics
    for service in config.services:
        print(f"Querying service {service.name}")

        # Get raw data for the service metrics
        data_matrix = client.read_all_database_metrics_default(service)
        
        # Add compliance checks for time-related metrics
        complete_matrix = add_time_threshold_columns(data_matrix, service)
        
        # Direct ouput to the selected channels
        output_manager.default_output(service.name, complete_matrix, timeframe="DEFAULT")

        # Since calculated metrics are also included, find if they exist
        if service.has_calculated_metrics():
            
            # Get raw data from the calculated metrics
            calc_matrix = client.read_all_calculated_service_metrics_default(service)
            
            # Add compliance checks for time-related metrics
            calc_complete = add_time_threshold_columns(calc_matrix, service)
            
            # Direct ouput to the selected channels
            output_manager.default_output(service.name, calc_complete, timeframe="CALC")
        
        else:
            print(f"Service {service.name} has no calculated metrics.")


def get_historical_database_metrics():
    
    # Get the global objects and the configuration
    client = get_dynatrace_client()
    output_manager = get_output_manager()
    config = get_config()

    for database in config.databases:
        print(f"\nQuerying database: {database.name}")

        # Get raw metric for the database
        data_matrix = client.read_all_database_metrics_default(database)
        
        # Direct output to the selected channels
        output_manager.default_output(database.name, data_matrix, timeframe="DEFAULT")


def start_last_trx_polling():
    poller = get_poller()
    output_manager = get_output_manager()

    print("Starting last transaction polling... press CTRL + C to interrupt")

    try:
        while True:
            # Get current time to maintain regular interval
            last_poll = datetime.now()

            # Poll the last transaction
            transaction_poll = poller.poll_last_transaction()

            # Output results
            output_manager.last_trx_poll_output(transaction_poll)

            # Calculate remaining time before next poll
            processing_time = (datetime.now() - last_poll).total_seconds()
            remaining_time = max(0, 30 - processing_time)

            # Wait before next poll
            time.sleep(remaining_time)           

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return False
    except Exception as e:
        print(f"Polling error with message: {str(e)}")
        return True
    finally:
        output_manager.finalize_last_trx_poll_files()
        


def start_service_polling():

    print("Starting service polling... press CTRL + C to interrupt")

    # Get poller
    poller = get_poller()
    
    # Get output manager
    output_manager = get_output_manager()

    # Get configuration
    config = get_config()

    # Get config parameters to echo
    from_time = config.polling.from_time
    to_time = config.polling.to_time
    resolution = config.polling.resolution

    print (f"Polling configuration, from: {from_time}, to: {to_time}, resolution: {resolution}")
    
    # Create list of time-based metrics
    metrics_by_service = defaultdict(list)

    # Add a list of metrics by service
    for metric in poller.metrics:
        metrics_by_service[metric.service_name].append(metric)

    try:
        while True:
            # Get the list of all the selected metrics for each service name
            for service_name, metrics in metrics_by_service.items():
                current_time = datetime.now()
                print(f"Polling metrics from service: {service_name}... at time {current_time}")

                stats_pairs: List[Tuple[str, PollingStats]] = []

                # For each metric
                for metric in metrics:
                    # Poll the metric and get the stats
                    stats = poller.poll_metric_from_service(metric)
                    # Add to the pair {metric_name, stats}
                    stats_pairs.append((metric.metric_name, stats))
                
                # Direct output to selected writers (via output manager)
                output_manager.service_poll_output(service_name, stats_pairs)
                print(f"Finished polling service {service_name}")

            print("Polling complete... waiting 30 seconds...")
            print (f"Polling configuration, from: {from_time}, to: {to_time}, resolution: {resolution}")
            time.sleep(30)

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"Polling error with message: {str(e)}")
    finally:
        for service_name, _ in metrics_by_service.items():
            output_manager.finalize_polling_file(service_name)
    

def add_time_threshold_columns(matrix, service):
    """
    Adds threshold compliance columns next to time-related metrics in the matrix.
    Automatically detects columns containing 'Time' or 'time' (case insensitive),
    excluding 'Timestamp'.
    
    Args:
        matrix: The data matrix (header + rows)
        service: The service object containing threshold_ms
    
    Returns:
        New matrix with threshold compliance columns added
    """
    print("Adding threshold compliance calculations...")

    if not matrix or len(matrix) < 2:  # Needs at least header and one data row
        return matrix
    
    header = matrix[0]
    new_matrix = [header.copy()]
    threshold_ms = service.threshold_ms  # Directly access threshold from service
    
    # Find time-related columns (case insensitive, excluding 'Timestamp')
    time_columns = []
    for i, col_name in enumerate(header):
        if (i == 0 and col_name == "Timestamp"):
            continue  # Skip timestamp column
        if "time" in col_name.lower() and "timestamp" not in col_name.lower():
            time_columns.append(i)
    
    if not time_columns:
        return matrix  # No time metrics found
    
    # Insert new threshold columns (working backwards to maintain positions)
    for col_pos in sorted(time_columns, reverse=True):
        original_name = header[col_pos]
        new_col_name = f"{original_name} Compliance"
        new_matrix[0].insert(col_pos + 1, new_col_name)
    
    # Process data rows
    for row in matrix[1:]:
        new_row = row.copy()
        
        # Insert threshold values (working backwards)
        for col_pos in sorted(time_columns, reverse=True):
            time_value = row[col_pos]
            
            # Default to compliant (1) if empty/None
            if time_value in (None, "", "N/A", "NaN"):
                complies = 1
            else:
                try:
                    time_ms = float(time_value) * 1000  # Convert to milliseconds
                    complies = 1 if time_ms <= threshold_ms else 0
                except (ValueError, TypeError):
                    complies = 1  # Default to compliant if parsing fails
            
            new_row.insert(col_pos + 1, int(complies))
        
        new_matrix.append(new_row)
    
    return new_matrix

       
if __name__ == "__main__":
    main()

