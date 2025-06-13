from config_loader import get_config
from debugger import Debugger
from dynatrace_client import get_dynatrace_client
from output_stream.output_manager import OutputManager
from clients.synth_monitor import get_synth_monitor_client


def main():
    print("Synthetic monitoring test")

    client = get_dynatrace_client()

    abono_mercado_pago = "HTTP_CHECK-8BEE0BF63C2C4D4D"
    abono_promedio = "HTTP_CHECK-5318DC3B9571D311"

    try:
        synth_client = get_synth_monitor_client()
    except Exception as e:
        print(f"There was a error attempting to fetch the synthetic monitor client: {str(e)}")

    # Debugger.echo_synth_monitor_client_config()
    monitor = synth_client.get_monitor_parameters_by_id(abono_mercado_pago)

    print("Setting new timeout...\n")
    monitor.set_timeout(60)

    success = synth_client.update_monitor_parameters_by_id(abono_mercado_pago, monitor)
    if success:
        print(f"Successfully updated monitor")
    else:
        print("Update unsuccesful")


    
    print("\nTHE END")

    # service_name = "KLAP CL"
    # service_id = "SYNTHETIC_TEST-6D53466B35B2E9F5"

    # metric = "builtin:synthetic.browser.totalDuration"
    # metric = "builtin:synthetic.browser.availability"
    # metric = "builtin:synthetic.browser.success"
    # metric = "builtin:synthetic.browser.availability.location.total"
    # metric = "builtin:synthetic.browser.event.failure"
   
    # Calculated metric
    # metric = "calc:synthetic.browser.klapclflujo.visuallycomplete"
    # metric = "calc:synthetic.browser.klapclflujo.visuallycomplete_cargarklap"
    # metric = "calc:synthetic.browser.klapclflujo.visuallycomplete_portalcomercio"
    metric = "calc:synthetic.browser.klapclflujo.visuallycomplete_cerrarsesion"
     
    # client.test_service_metrics(metric, service_name, service_id, "1m", "now-15m", "now", time_based=False)


def update_token_in_monitor(monitor_id: str):
    # GET monitor parameters (Monitor Client)

    # Assign monitor parameters to object

    # Get new token (not authorize, token must be fresh)

    # PUT monitor parameters
    
    pass


if __name__ == "__main__":
    main()