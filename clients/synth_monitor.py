import requests
import json
from dotenv import load_dotenv
import os
from typing import List, Optional, Dict, Union, Any
from datetime import datetime

load_dotenv()

class MonitorRequestConfig:
    def __init__(self, data: Dict[str, Any]):
        self.description = data.get("description")
        self.url = data.get("url")
        self.method = data.get("method")
        self.requestBody = data.get("requestBody")
        self.validation = data.get("validation", {})
        self.configuration = data.get("configuration", {})
        self.requestTimeout = data.get("requestTimeout")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "url": self.url,
            "method": self.method,
            "requestBody": self.requestBody,
            "validation": self.validation,
            "configuration": self.configuration,
            "requestTimeout": self.requestTimeout
        }
    
    @classmethod
    def from_json(cls, json_data: Union[str, Dict[str, Any]]) -> 'MonitorRequestConfig':
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        return cls(data)
    
    def to_json(self, pretty: bool = False) -> str:
        if pretty:
            return json.dumps(self.to_dict(), indent=2)
        return json.dumps(self.to_dict())
    
    def update_request_date(self):
        """Update the request date to use today's date."""
        if self.requestBody:
            try:
                body_data = json.loads(self.requestBody)
                today = datetime.now().strftime("%Y-%m-%d")
                body_data["start_date"] = today
                body_data["end_date"] = today
                self.requestBody = json.dumps(body_data, indent=4)
            except json.JSONDecodeError:
                pass



class MonitorScript:
    def __init__(self, data: Dict[str, Any]):
        self.version = data.get("version")
        self.requests = [MonitorRequestConfig(req) for req in data.get("requests", [])]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "requests": [r.to_dict() for r in self.requests]
        }
    
    @classmethod
    def from_json(cls, json_data: Union[str, Dict[str, Any]]) -> 'MonitorScript':
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        if not isinstance(data.get("requests", []), list):
            raise ValueError("Requests must be a list")
            
        requests = [MonitorRequestConfig.from_json(req) for req in data.get("requests", [])]
        return cls({
            "version": data.get("version"),
            "requests": requests
        })
    
    def to_json(self, pretty: bool = False) -> str:
        if pretty:
            return json.dumps(self.to_dict(), indent=2)
        return json.dumps(self.to_dict())


class SyntheticMonitor:
    def __init__(self, data: Dict[str, Any]):
        self.entityId = data.get("entityId")
        self.name = data.get("name")
        self.frequencyMin = data.get("frequencyMin")
        self.enabled = data.get("enabled")
        self.type = data.get("type")
        self.createdFrom = data.get("createdFrom")
        self.script = MonitorScript(data.get("script", {}))
        self.locations = data.get("locations", [])
        self.anomalyDetection = data.get("anomalyDetection", {})
        self.tags = data.get("tags", [])
        self.managementZones = data.get("managementZones", [])
        self.automaticallyAssignedApps = data.get("automaticallyAssignedApps", [])
        self.manuallyAssignedApps = data.get("manuallyAssignedApps", [])
        self.requests = data.get("requests", [])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entityId": self.entityId,
            "name": self.name,
            "frequencyMin": self.frequencyMin,
            "enabled": self.enabled,
            "type": self.type,
            "createdFrom": self.createdFrom,
            "script": self.script.to_dict(),
            "locations": self.locations,
            "anomalyDetection": self.anomalyDetection,
            "tags": self.tags,
            "managementZones": self.managementZones,
            "automaticallyAssignedApps": self.automaticallyAssignedApps,
            "manuallyAssignedApps": self.manuallyAssignedApps,
            "requests": self.requests
        }
    
    @classmethod
    def from_json(cls, json_data: Union[str, Dict[str, Any]]) -> 'SyntheticMonitor':
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        # Validate required fields
        required_fields = ["entityId", "name", "type"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Handle nested objects
        script_data = data.get("script", {})
        if not isinstance(script_data, dict):
            raise ValueError("Script must be a dictionary")
            
        return cls({
            "entityId": data["entityId"],
            "name": data["name"],
            "frequencyMin": data.get("frequencyMin"),
            "enabled": data.get("enabled", True),
            "type": data["type"],
            "createdFrom": data.get("createdFrom"),
            "script": script_data,
            "locations": data.get("locations", []),
            "anomalyDetection": data.get("anomalyDetection", {}),
            "tags": data.get("tags", []),
            "managementZones": data.get("managementZones", []),
            "automaticallyAssignedApps": data.get("automaticallyAssignedApps", []),
            "manuallyAssignedApps": data.get("manuallyAssignedApps", []),
            "requests": data.get("requests", [])
        })
    
    def to_json(self, pretty: bool = False) -> str:
        if pretty:
            return json.dumps(self.to_dict(), indent=2)
        return json.dumps(self.to_dict())

    def set_timeout(self, timeout_seconds: int):
        for req in self.script.requests:
            req.requestTimeout = timeout_seconds

    def enable_monitor(self):
        self.enabled = True

    def disable_monitor(self):
        self.enabled = False

class SynthMonitorClient:
    def __init__(
            self,
            environment_url_v1: str,
            environment_url_v2: str,
            configuration_url: str,
            user_token: str,
            monitor_admin_token: str
        ):
        self.environment_url_v1 = environment_url_v1
        self.environment_url_v2 = environment_url_v2
        self.configuration_url = configuration_url
        self.user_token = user_token
        self.monitor_admin_token = monitor_admin_token

    def get_monitor_parameters_by_id(self, monitor_id: str) -> Optional[SyntheticMonitor]:
        # Using synthetic monitor endpoint.
        # It belong the the API v1
        endpoint_url = f"{self.environment_url_v1}{os.getenv("MONITOR_PARAMETERS_ENDPOINT")}"
        
        # The URL requires the monitor ID for the call
        full_url = f"{endpoint_url}{monitor_id}"

        headers = {
            "Authorization": f"Api-Token {self.monitor_admin_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.get(full_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return SyntheticMonitor.from_json(data)
        elif response.status_code == 404:
            print(f"Monitor with ID {monitor_id} not found.")
            return None
        else:
            print(f"Failed to get monitor {monitor_id}, {response.text}")

    def update_monitor_parameters_by_id(
            self,
            monitor_id: str,
            monitor: SyntheticMonitor,
            etag: Optional[str] = None
            ) -> bool:
        # Using synthetic monitor endpoint.
        # It belong the the API v1
        endpoint_url = f"{self.environment_url_v1}{os.getenv("MONITOR_PARAMETERS_ENDPOINT")}"
        
        # The URL requires the monitor ID for the call
        full_url = f"{endpoint_url}{monitor_id}"

        headers = {
            "Authorization": f"Api-Token {self.monitor_admin_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Add ETag header if provided (for concurrency control)
        if etag:
            headers['If-Match'] = etag

        monitor_data = monitor.to_json(False)

        try:
            # Call PUT operation
            response = requests.put(full_url, headers=headers, data=monitor_data)

            # Handle success or failure
            if response.status_code == 204:
                print(f"Successfully updated monitor {monitor_id}")
                return True
            elif response.status_code == 404:
                print(f"Monitor {monitor_id} not found")
                return False
            elif response.status_code == 412:
                print(f"Update failed - the monitor was modified since the last retrieval")
                return False
            else:
                print(f"Failed to update monitor {monitor_id}")
                print(f"Status: {response.status_code} - Response: {response.text}")
                return False
            
        except requests.exceptions.RequestException as e:
            print(f"Reques failed: {str(e)}")
            return False


# This is the client
_synth_monitor_client_instance: Optional[SynthMonitorClient] = None

def get_synth_monitor_client():
    global _synth_monitor_client_instance

    # If the instance has not yet been created
    if _synth_monitor_client_instance is None:

        # Obtain values from environment
        environment_url_v1 = os.getenv("MONITOR_ENVIRONMENT_V1_URL")
        environment_url_v2 = os.getenv("MONITOR_ENVIRONMENT_V2_URL")
        configuration_url = os.getenv("DYNATRACE_CONFIGURATION_URL")
        user_token = os.getenv("DYNATRACE_API_TOKEN")
        monitor_admin_token = os.getenv("DYNATRACE_MONITOR_ADMIN_API_TOKEN")

        # If any of the environment values are not included
        if None in (
            environment_url_v1,
            environment_url_v2,
            configuration_url,
            user_token,
            monitor_admin_token
        ):
            # Add the missing values to list
            missing = []
            if environment_url_v1 is None: missing.append("MONITOR_ENVIRONMENT_V1_URL")
            if environment_url_v2 is None: missing.append("MONITOR_ENVIRONMENT_V2_URL")
            if configuration_url is None: missing.append("DYNATRACE_CONFIGURATION_URL")
            if user_token is None: missing.append("DYNATRACE_API_TOKEN")
            if monitor_admin_token is None: missing.append("DYNATRACE_MONITOR_ADMIN_API_TOKEN")
            # Raise and error (creation fails)
            raise RuntimeError(
                f"Missing configuration parameters {', '.join(missing)}\n"
                "Check your configuration"
            )
        
        # Create monitor client
        _synth_monitor_client_instance = SynthMonitorClient(
            environment_url_v1=environment_url_v1,
            environment_url_v2=environment_url_v2,
            configuration_url=configuration_url,
            user_token=user_token,
            monitor_admin_token=monitor_admin_token
        )

    return _synth_monitor_client_instance



