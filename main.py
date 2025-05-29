from config_loader import get_config
from debugger import Debugger
from dynatrace_client import get_dynatrace_client

def main():

    # Obtain configuration
    config = get_config()

    print(f"Debug mode: {config.debug}")

    if config.debug:
        Debugger.echo_configuration()
        
    client = get_dynatrace_client()
    client.get_service_metrics("Metric 1")

       

if __name__ == "__main__":
    main()

