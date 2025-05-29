from config_loader import get_config
from dotenv import load_dotenv
import os

# dynatrace_client.py
class DynatraceClient:
    def __init__(self, token, base_url):
        self.token = token
        self.base_url = base_url

    def get_service_metrics(self, service_id):
        print(f"We are here - {service_id}")
        pass  # implement API call

    def get_database_metrics(self, db_id):
        pass  # implement API call

    def poll_service(self, service_id):
        pass  # implement polling logic

# -- Singleton access --
_client = None

def get_dynatrace_client():
    global _client

    if _client is None:
        config = get_config()
        load_dotenv()
        _client = DynatraceClient(os.getenv("DYNATRACE_API_TOKEN"), os.getenv("DYNATRACE_URL"))
    return _client
