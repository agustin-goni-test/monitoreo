from config_loader import get_config
from debugger import Debugger
from dynatrace_client import get_dynatrace_client
from output_stream.output_manager import OutputManager
from clients.synth_monitor import get_synth_monitor_client, SyntheticMonitor
from clients.login import get_login_client
from time import sleep



def main():
    print("Synthetic monitoring test")

    # client = get_dynatrace_client()
    login = get_login_client()

    # abono_mercado_pago = "HTTP_CHECK-8BEE0BF63C2C4D4D"
    abono_promedio = "HTTP_CHECK-5318DC3B9571D311"

    success = initialize_monitor(abono_promedio)

    if success:
        while True:
            try:
                token_needed = login.token_refresh_needed()
                if not token_needed:
                    print("No need to update the token for now")
                else:
                    print("Token must be updated")
                    update_header_in_monitor(abono_promedio)
                sleep(30)
            except KeyboardInterrupt:
                print("\nInterrupted by user.")
            except Exception as e:
                print(f"Polling error with message: {str(e)}")
    else:
        print("Monitor initialization has failed... aborting.")




    # try:
    #     synth_client = get_synth_monitor_client()
    # except Exception as e:
    #     print(f"There was a error attempting to fetch the synthetic monitor client: {str(e)}")

    # # Debugger.echo_synth_monitor_client_config()
    # monitor = synth_client.get_monitor_parameters_by_id(abono_mercado_pago)

    # # new_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIiLCJpc3MiOiJBdXRoU2VjdXJpdHlXZWIiLCJzdWIiOiIwOTc0MzA0My04IiwiaWF0IjoxNzQ5ODI0NDg5LCJleHAiOjE3NDk4NTMyODksImF1dGhvcml0aWVzIjpbXSwic2Vzc2lvbl9kYXRhIjoie1widXNlcl9pZFwiOjY1NTEzLFwic2Vzc2lvbl9pZFwiOlwiYklLd1Npc0I3RHhBVlhWSVlJN3czeFZlcWxsT3ZsTmdcIixcImFjY2Vzc2VzXCI6MH0iLCJuYW1lIjoiIiwiZW1haWwiOiIiLCJjb3JlX3Rva2VuIjoiZXlKMGVYQWlPaUpLVjFRaUxDSmhiR2NpT2lKSVV6STFOaUo5LmV5SnFkR2tpT2lJMk5HTTFNek13WmpCaU9UWTBZalV3T1RRek56WmxNR1prWm1WbE9EbGtPU0lzSW1semN5STZJa0YxZEdoVFpXTjFjbWwwZVZkbFlpSXNJbk4xWWlJNklqQTVOelF6TURRekxUZ2lMQ0pwWVhRaU9qRTNORGs0TWpRME9Ea3NJbVY0Y0NJNk1UYzBPVGcxTXpJNE9Td2ljMlZ6YzJsdmJsOWtZWFJoSWpvaWUxd2lkWE5sY2w5cFpGd2lPalkxTlRFekxGd2ljMlZ6YzJsdmJsOXBaRndpT2x3aVlrbExkMU5wYzBJM1JIaEJWbGhXU1ZsSk4zY3plRlpsY1d4c1QzWnNUbWRjSWl4Y0ltRmpZMlZ6YzJWelhDSTZNSDBpTENKdVlXMWxJam9pSWl3aVpXMWhhV3dpT2lJaWZRLjhZOUN1UThrQmtuQmFtOG04MHRUb0Fpald6aVp4aWozMy02VHpnWldYLVkiLCJ1c2VyX25hbWUiOiIwOTc0MzA0My04IiwiY2xpZW50X2lkIjoiIiwic2NvcGUiOltdfQ.DPEmbZHAaFLVEPdhalnJHNlstZH_Z8M-UEe2GJmfwDQ"

    # new_token = login.refresh_token()

    # # Update token

    # new_monitor = monitor
    
    # for request in new_monitor.script.requests:
    #     # Find the Authorization header
    #     for header in request.configuration.get('requestHeaders', []):
    #         if header.get('name') == 'Authorization':
    #             header['value'] = f"Bearer {new_token}"
    #             break

    # print(new_monitor.to_json(True))

    # success = synth_client.update_monitor_parameters_by_id(abono_mercado_pago, monitor)
    # if success:
    #     print(f"Successfully updated monitor")
    # else:
    #     print("Update unsuccesful")


    
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


def initialize_monitor(monitor_id: str) -> bool:
    
    # Get synthetic monitor client
    try:
        synth_client = get_synth_monitor_client()
    except Exception as e:
        print(f"There was a error attempting to fetch the synthetic monitor client: {str(e)}")
    
    # Initialize login client and authenticate
    login = get_login_client()
    token = login.authenticate()

    # Get the parameters for the monitor
    monitor = synth_client.get_monitor_parameters_by_id(monitor_id)

    # Add the initilization token to the monitor's headers
    # (regardless of what it had before)
    new_monitor = update_header_in_monitor(token, monitor)

    # Update the monitor's parameters with the token
    success = synth_client.update_monitor_parameters_by_id(monitor_id, new_monitor)
    if success:
        print(f"Monitor {monitor_id} has been initialized successfully")
        return True
    else:
        print(f"Failed to initialize monitor {monitor_id}")
        return False


def update_token_in_monitor(monitor_id: str):
    
    try:
        synth_client = get_synth_monitor_client()
    except Exception as e:
        print(f"There was a error attempting to fetch the synthetic monitor client: {str(e)}")

    login_client = get_login_client()

    # GET monitor parameters (Monitor Client)
    monitor = synth_client.get_monitor_parameters_by_id(monitor_id)

    # Get new token (not authorize, token must be fresh)
    new_token = login_client.refresh_token()
    new_monitor = update_header_in_monitor(new_token, monitor)

    # PUT monitor parameters
    success = synth_client.update_monitor_parameters_by_id(monitor_id, new_monitor)
    if success:
        print(f"Successfully updated monitor")
    else:
        print("Update unsuccesful")

    

def update_header_in_monitor(new_token: str, monitor: SyntheticMonitor) -> SyntheticMonitor:
    new_monitor = monitor

    for request in new_monitor.script.requests:
        # Find the Authorization header
        for header in request.configuration.get('requestHeaders', []):
            if header.get('name') == 'Authorization':
                header['value'] = f"Bearer {new_token}"
                break

    return new_monitor 


if __name__ == "__main__":
    main()