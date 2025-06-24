from config_loader import get_config
from debugger import Debugger
from dynatrace_client import get_dynatrace_client
from output_stream.output_manager import OutputManager
from clients.synth_monitor import get_synth_monitor_client, SyntheticMonitor
from clients.login import get_login_client
from time import sleep


def main():
    print("Synthetic monitoring test")

    client = get_dynatrace_client()
    # login = get_login_client()

    # abono_mercado_pago = "HTTP_CHECK-8BEE0BF63C2C4D4D"
    abono_promedio = "HTTP_CHECK-5318DC3B9571D311"

    # sleep_monitor(abono_promedio)

    print("OK")

    # sleep_monitor(abono_promedio)

    # manage_synthetic_monitor(abono_promedio)

    # success = True
    # success = initialize_monitor(abono_promedio)

    # if not success:
    #     print("There was an error")

    # while success:
    #     try:
    #         token_needed = login.token_refresh_needed()
    #         if not token_needed:
    #             print("No need to update the token for now")
    #         else:
    #             print("Token must be updated")
    #             update_token_in_monitor(abono_promedio)
    #         sleep(30)
    #     except KeyboardInterrupt:
    #         print("\nInterrupted by user.")
    #         success = False
    #     except Exception as e:
    #         print(f"Polling error with message: {str(e)}")
    #         success = False

    




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

    service_name = "KLAP-CL"
    service_id = "SYNTHETIC_TEST-6D53466B35B2E9F5"

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
     
    client.test_service_metrics(metric, service_name, service_id, "15m", "now-7d", "now", time_based=False)




def concurrent_manage_monitor(monitor_id: str, stop_event):
    """This method is used to handle concurrency in updating the monitor.
    
    This method is initiated as a separate thread. The stop event signals
    a thread stop. Inside, it sends a call to protected_manage_monitor()
    and sleeps the thread for a set number of seconds (or the interruption)"""

    # Currently this method takes 1 monitor id. It could be modified to take several

    # Repeat as long as there is no stop event
    while not stop_event.is_set():
        try:
            # Call inside method that has the logic
            # This call could be looped for seveal monitors
            protected_manage_monitor(monitor_id)

            # Sleep the process for a set time (unless interrupted)
            sleep_with_interrupt(300, stop_event)

        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            break
        except Exception as e:
            print(f"Polling error with message: {str(e)}")
            continue


def protected_manage_monitor(monitor_id):
    """This method is the inside call for the concurrent implementation
    of the synthetic monitor update.
    
    It doesn't directly manage an interruption, as the "parent" method,
    concurrent_manage_monitor(), is the one that handles the thread itself."""
    
    # Get login client
    login = get_login_client()

    try:
        # Find if we need to refresh the token (based on expiration time)
        token_needed = login.token_refresh_needed()

        # If we don't need to refresh the token, do nothing
        if not token_needed:
            print(f"No need to update the monitor {monitor_id} for now.")

        # If we need to update the token, call the method that updates it.
        else:
            print(f"Token for monitor {monitor_id} must be updated.")
            update_token_in_monitor(monitor_id)

    except Exception as e:
        print(f"Polling error with message: {str(e)}")
        


def sleep_with_interrupt(seconds, stop_event):
    """This method allows to sleep a thread conditionally. This helps
    to interrupt right away when the stop signal comes."""
    for _ in range(int(seconds * 10)):  # check every 0.1s
        if stop_event.is_set():
            break
        sleep(0.1)


def manage_synthetic_monitor(monitor_id: str):
    """This method allows to permanently manage the continuity of a monitor.
    
    This is the non-concurrent version. We can use it in isolation only.
    In case we need concurrency, we must use concurrent_manage_monitor"""

    # Get the login handler
    login = get_login_client()

    # Initialize the monitor (adding a new token and today's date)
    # success = initialize_monitor(monitor_id)
    success = True

    if not success:
        print("There was an error...")

    # This parameter is here in case we need initialization
    while success:
        try:
            # Determine if we need a new token (based on expiration time)
            token_needed = login.token_refresh_needed()

            # If we don't need it, do nothing
            if not token_needed:
                print("No need to update the token for now")

            # If we need a new token, call the method that updates it
            else:
                print("Token must be updated")
                update_token_in_monitor(monitor_id)
            
            # Wait a set number of seconds
            sleep(30)

        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            success = False
        except Exception as e:
            print(f"Polling error with message: {str(e)}")
            success = False


def initialize_monitor(monitor_id: str) -> bool:
    """This method initializes a monitor by ID.
    
    It assumes there is no valid token, and therefores starts by authenticating."""

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

    # Update date as well, in case it's not today's
    for request in new_monitor.script.requests:
        request.update_request_date()

    # Make sure the monitor is enabled
    new_monitor.enabled = True

    # Update the monitor's parameters with the token
    success = synth_client.update_monitor_parameters_by_id(monitor_id, new_monitor)
    if success:
        print(f"Monitor {monitor_id} has been initialized successfully")
        return True
    else:
        print(f"Failed to initialize monitor {monitor_id}")
        return False
    

def force_initialize_monitor(monitor_id) -> str:
    """The purpose of this method is to be able to initialize a monitor
    with a specific token (the one found in the .env file).
    
    This is useful for testing, because the normal initialization method, when
    starting from scratch, will get a new token. Since there is a max number
    of token a user can have, getting a new token with each test can be costly."""

    print(f"Force initializing monitor {monitor_id}...")

    # Get synthetic monitor client
    try:
        synth_client = get_synth_monitor_client()
    except Exception as e:
        print(f"There was a error attempting to fetch the synthetic monitor client: {str(e)}")
    
    # Get login client
    login = get_login_client()
    
    # Force to use the token from the environment variable
    token = login.get_token_from_env()
    print("Using token obtained from environment variable...")

    # Get the parameters for the monitor
    monitor = synth_client.get_monitor_parameters_by_id(monitor_id)

    # Add the initilization token to the monitor's headers
    # (regardless of what it had before)
    new_monitor = update_header_in_monitor(token, monitor)
    print("Token has been updated in monitor definition...")

    # Update the monitor's parameters with the token
    success = synth_client.update_monitor_parameters_by_id(monitor_id, new_monitor)
    if success:
        print(f"Monitor {monitor_id} has been initialized successfully")
        return True
    else:
        print(f"Failed to initialize monitor {monitor_id}")
        return False

    
def sleep_monitor(monitor_id: str) -> bool:
    """This method disables a monitor so it won't continue executing. We use
    it to sleep the monitor when updatind the token is not possible in practice.
    This prevents the monitor from failing constantly when the token expires."""
    
    # Get synthetic monitor client
    try:
        synth_client = get_synth_monitor_client()
    except Exception as e:
        print(f"There was a error attempting to fetch the synthetic monitor client: {str(e)}")

    monitor = synth_client.get_monitor_parameters_by_id(monitor_id)
    
    # Disable monitor
    monitor.enabled = False

    # Update the monitor's parameters with the token
    success = synth_client.update_monitor_parameters_by_id(monitor_id, monitor)
    if success:
        print(f"Monitor {monitor_id} was successfully disabled")
        return True
    else:
        print(f"Failed to disable monitor {monitor_id}")
        return False



def update_token_in_monitor(monitor_id: str):
    """This method updates the token in the monitor by using the Dyantrace API.
    
    Using the monitor ID, it GETs the monitor parameters, modifies the header for
    authorization, and PUTs the new parameters."""
    
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
    """This method uses a JSON representation of the parameters of the monitor and
    updates the authorizarion header to include a new token"""
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