from config_loader import get_config
from debugger import Debugger
from dynatrace_client import get_dynatrace_client
from output_stream.output_manager import OutputManager
from polling.poller import Poller

def main():

    # Obtain configuration
    config = get_config()
    
    # Create poller
    poller = Poller()

    print(f"Debug mode: {config.debug}")

    if config.debug:
        Debugger.echo_configuration()
        poller.echo_configuration()

        
    client = get_dynatrace_client()
    output_manager = OutputManager()

    # metric_name = 'calc:service.requestcount_abonos_byrange'
    # metric_name = 'calc:service.responsetimecaller_abonos_byrange'
    # metric_name = 'calc:service.requestcount_trxmediospago_filterdetails'
    # metric_name = 'calc:service.responsetime_trxmediospago_filterdetails'
    # metric_name = 'calc:service.requestcount_trxmediospago_filterdetails'


    # Para servicio de Abonos
    # client.test_service_metrics(metric_name, "AbonosController", "SERVICE-123E236BA4855F4A", time_based=True)

    # Para servicio de transacciones
    # client.test_service_metrics(metric_name, "AbonosController", "SERVICE-FD9343224D905203", time_based=False)

    # for service in config.services:
    #     print(f"\nQuerying service: {service.name}")
        
    #     data_matrix = client.read_all_service_metrics_default(service)
    #     complete_matrix = add_time_threshold_columns(data  _matrix, service)
    #     output_manager.default_output(service.name, complete_matrix)

    #     if service.has_calculated_metrics():
    #         data_matrix2 = client.read_all_calculated_service_metrics_default(service)
    #         complete_matrix2 = add_time_threshold_columns(data_matrix2, service)
    #         output_manager.default_output(service.name, complete_matrix2)
    #     else:
    #         print(f"Service {service.name} does not have any calculated metrics.")

    # for database in config.databases:
    #     print(f"\nQuerying database: {database.name}")

    #     data_matrix = client.read_all_database_metrics_default(database)
    #     output_manager.default_output(database.name, data_matrix)


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

