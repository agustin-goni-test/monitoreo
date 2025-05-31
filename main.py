from config_loader import get_config
from debugger import Debugger
from dynatrace_client import get_dynatrace_client
from output_stream.output_manager import OutputManager

def main():

    # Obtain configuration
    config = get_config()

    print(f"Debug mode: {config.debug}")

    if config.debug:
        Debugger.echo_configuration()
        
    client = get_dynatrace_client()

    # metric_name = 'calc:service.requestcount_abonos_byrange'
    # metric_name = 'calc:service.responsetimecaller_abonos_byrange'
    # metric_name = 'calc:service.requestcount_trxmediospago_filterdetails'
    # metric_name = 'calc:service.responsetime_trxmediospago_filterdetails'
    # metric_name = 'calc:service.requestcount_trxmediospago_filterdetails'


    # Para servicio de Abonos
    # client.test_service_metrics(metric_name, "AbonosController", "SERVICE-123E236BA4855F4A", time_based=True)

    # Para servicio de transacciones
    # client.test_service_metrics(metric_name, "AbonosController", "SERVICE-FD9343224D905203", time_based=False)

    for service in config.services:
        print(f"\nQuerying service: {service.name}")
        
        data_matrix = client.read_all_service_metrics(service)
        output_manager = OutputManager()
        output_manager.default_output(service.name, data_matrix)

        

       

if __name__ == "__main__":
    main()

