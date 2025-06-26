from config_loader import get_config
from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timezone
import json

# dynatrace_client.py
class DynatraceClient:
    def __init__(self, token, base_url):
        self.token = token
        self.base_url = base_url
        self.config = get_config()

    
    # This method queries the service metric with the default configuration.
    # That is, the configuration indicated in the YAML file (default parameters).
    def get_service_metrics_default(self, service_id, service_name, metric):
        
        # Get default parameters from configuration
        resolution = self.config.timeframes["services"].resolution
        from_time = self.config.timeframes["services"].from_time
        to_time = self.config.timeframes["services"].to_time

        # Get the service metrics and return result to original caller
        return self.get_service_metrics(service_id, service_name, metric, resolution, from_time, to_time)
    
    # Get the service metrics for the previous 24 hours
    def _get_service_metrics_day(self, service_id, service_name, metric):
        
        # Set parameters
        resolution = "1m"
        from_time = "now-1d"
        to_time = "now"

        # Get the service metrics and return result to original caller
        return self.get_service_metrics(service_id, service_name, metric, resolution, from_time, to_time)
        
    # Get the service metrics for the previous 7 days
    def _get_service_metrics_week(self, service_id, service_name, metric):
        
        # Set parameters
        resolution = "1m"
        from_time = "now-7d"
        to_time = "now"

        # Get the service metrics and return result to original caller
        return self.get_service_metrics(service_id, service_name, metric, resolution, from_time, to_time)

    # Get the service metrics for the previous 27 days (due to data limitations)
    def _get_service_metrics_month(self, service_id, service_name, metric):
        
        # Set parameters
        resolution = "5m"
        from_time = "now-27d"
        to_time = "now"

        # Get the service metrics and return result to original caller
        return self.get_service_metrics(service_id, service_name, metric, resolution, from_time, to_time)

    # get the service metrics for the previous year
    def _get_service_metrics_year(self, service_id, service_name, metric):
        
        # Set parameters
        resolution = "1h"
        from_time = "now-365d"
        to_time = "now"

        # Get the service metrics and return result to original caller
        return self.get_service_metrics(service_id, service_name, metric, resolution, from_time, to_time)
    
    # This method is a generic metric query, with any combination of resolution and timespan
    def get_service_metrics(self, service_id, service_name, metric, resolution, from_time, to_time):
        """Implement a query to obtain a metric from a service in the given timefram"""
        # Set up call
        url = self.base_url
        headers = {
            'Authorization': f'Api-Token {self.token}'
        }
        params = {
            'metricSelector': metric,
            'resolution': resolution,
            'entitySelector': f'entityId({service_id})',
            'from': from_time,
            'to': to_time
        }

        # Echo parameters if needed for debugging
        if self.config.debug:
            print(f"We are here - {service_name} - {service_id}")
            print(f'URL: {self.base_url}')
            print(f'Token: {self.token}')
            print(params)  

        # Call API
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        # Call the parser
        data_matrix = self._parse_metric_response(response)

        # Return a results matrix
        return data_matrix
    
    # This method is used to separate the query database metrics with their own default parameters
    def read_all_database_metrics_default(self, service):
        print(f"Getting metrics for database {service.name} for default period...")
        period = "DATABASE_DEFAULT"
        return self._read_all_service_metrics(service, period)

    # This method is used to separate the query database metrics with their own default parameters
    def get_database_metrics(self, database_id, database_name, metric):

        # Get time parameters from configuration
        resolution = self.config.timeframes["databases"].resolution
        from_time = self.config.timeframes["databases"].from_time
        to_time = self.config.timeframes["databases"].to_time

        return self.get_service_metrics(database_id, database_name, metric, resolution, from_time, to_time)


    def poll_service(self, service_id):
        pass  # implement polling logic

    def read_all_service_metrics_default(self, service):
        print(f"Getting metrics for service {service.name} for default period...")
        period = "default"
        return self._read_all_service_metrics(service, period, metric_source="metrics")
    
    def read_all_calculated_service_metrics_default(self, service):
        print(f"Getting calculated metrics for service {service.name} for default period...")
        period = "default"
        return self._read_all_service_metrics(service, period, metric_source="calculated_metrics")
    
    def read_all_service_metrics_day(self, service):
        print(f"Getting metrics for service {service.name} for DAY period...")
        period = "DAY"
        return self._read_all_service_metrics(service, period, metric_source="metrics")

    def read_all_service_metrics_week(self, service):
        print(f"Getting metrics for service {service.name} for WEEK period...")
        period = "WEEK"
        return self._read_all_service_metrics(service, period, metric_source="metrics")

    def read_all_service_metrics_month(self, service):
        print(f"Getting metrics for service {service.name} for MONTH period...")
        period = "MONTH"
        return self._read_all_service_metrics(service, period, metric_source="metrics")

    def read_all_service_metrics_year(self, service):
        print(f"Getting metrics for service {service.name} for YEAR period...")
        period = "YEAR"
        return self._read_all_service_metrics(service, period, metric_source="metrics")
    
    def _read_all_service_metrics(self, service, period, metric_source="metrics"):

        # Get the correct metrics dictionary
        metrics_to_use = getattr(service, metric_source, {})
        
        # Always return at least the header structure
        header = ["Timestamp"]
        for metric_name in metrics_to_use.keys():
            header.append(self._format_metric_header(metric_name))
        
        # Return early if no metrics
        if not metrics_to_use:
            return [header]

        metric_data = {}
        all_timestamps = set()

        # Fetch data for each metric
        for metric_name, metric_id in metrics_to_use.items():
            try:
                if period == "default":
                    metric_matrix = self.get_service_metrics_default(service.id, service.name, metric_id)
                elif period == "DAY":
                    # metric_matrix = self.get_service_metrics(service.id, service.name, metric_id, "1m", "now-1d", "now")
                    metric_matrix = self._get_service_metrics_day(service.id, service.name, metric_id)
                elif period == "WEEK":
                    # metric_matrix = self.get_service_metrics(service.id, service.name, metric_id, "1m", "now-7d", "now")
                    metric_matrix = self._get_service_metrics_week(service.id, service.name, metric_id)
                elif period == "MONTH":
                    metric_matrix = self._get_service_metrics_month(service.id, service.name, metric_id)
                elif period == "YEAR":
                    metric_matrix = self._get_service_metrics_year(service.id, service.name, metric_id)
                elif period == "DATABASE_DEFAULT":
                    metric_matrix = self.get_database_metrics(service.id, service.name, metric_id)     
                
                metric_type = self._get_metric_type(metric_name)
                
                for row in metric_matrix:
                    timestamp, value = row
                    formatted_value = self._format_metric_value(metric_type, value)
                    all_timestamps.add(timestamp)
                    metric_data.setdefault(timestamp, {})[metric_name] = formatted_value
            except Exception as e:
                print(f"Error processing metric {metric_name}: {str(e)}")
                continue

        # Build the final matrix
        data_matrix = [header]
        
        for timestamp in sorted(all_timestamps):
            readable_ts = self._format_timestamp(timestamp)
            row = [readable_ts]
            for metric_name in metrics_to_use.keys():
                value = metric_data.get(timestamp, {}).get(metric_name, "N/A")
                row.append(value)
            data_matrix.append(row)

        return data_matrix if len(data_matrix) > 1 else [header]
    
    # Helper method to format the timestamps
    def _format_timestamp(self, ts):
        # Convert milliseconds to seconds for datetime
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).astimezone()
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # Helper method to manage the texts in the header
    def _format_metric_header(self, metric_name: str) -> str:
        # Convert snake_case to Title Case
        readable_name = metric_name.replace('_', ' ').title()

        # Determine metric type
        metric_type = self._get_metric_type(metric_name)

        # Append suffix
        if metric_type == "time":
            readable_name += "(s)"
        elif metric_type == "rate":
            readable_name += "(%)"

        return readable_name

    
    def _get_metric_type(self, metric_name: str) -> str:
        """
        Determines the metric type based on the metric name.
        """
        name_lower = metric_name.lower()
        if "time" in name_lower:
            return "time"
        elif "count" in name_lower:
            return "count"
        elif "rate" in name_lower:
            return "rate"
        else:
            return "unknown"

    def _format_metric_value(self, metric_type: str, value):
        """
        Formats the metric value based on its type.
        """
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            return value  # If not a number, return as-is.

        if metric_type == "time":
            return numeric_value / 1_000_000  # Convert microseconds to seconds.
        elif metric_type == "rate":
            return numeric_value / 100  # Example: percent to fraction (adjust as needed).
        else:  # count or unknown
            return numeric_value

    

    def _parse_metric_response(self, response):   
        
        try:
            response_json = response.json()
        except ValueError:
            print("Response was not JSON!")
            print(response.text)
            return []

        result_data = response_json.get('result', [])

        timestamps_and_values = []
        for item in result_data:
            data_points = item.get('data', [])
            for point in data_points:
                timestamps = point.get('timestamps')
                values = point.get('values')
                for timestamp, value in zip(timestamps, values):
                    timestamps_and_values.append((timestamp, value))

        return timestamps_and_values

    def test_service_metrics(self, metric_name, service_name, service_id, resolution, from_time, to_time, time_based):
        """This method can test calling a specific metric and getting results"""

        print(f"Testing a call for service name: {service_name} and metric {metric_name}\n")
        print("Attempting to query the last 2 hours with a 1 minute resolution... \n\n")

        print(f'URL: {self.base_url}')
        print(f'Token: {self.token}')
        

        # Will implement a call to a specific calculated metric only

        url = self.base_url
        headers = {
            'Authorization': f'Api-Token {self.token}'
        }
        params = {
            'metricSelector': metric_name,
            'resolution': resolution,
            'entitySelector': f'entityId({service_id})',
            'from': from_time,
            'to': to_time
        }

        # params = {
        #     'metricSelector': 'calc%3Asynthetic.browser.klapclflujo.visuallycomplete'
        # }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        print(f"Raw data: {data}")



        # Remove later. This is only here to test the output
        import csv
        import os
        from datetime import datetime
        
        os.makedirs("output_files", exist_ok=True)
        csv_data = []  # Store data for CSV



        # Assuming your JSON is stored in a variable called 'data'
        for result in data.get('result', []):
            metric_id = result.get('metricId')
            print(f"\nMetric ID: {metric_id}")
            
            for entry in result.get('data', []):
                timestamps = entry.get('timestamps', [])
                values = entry.get('values', [])
                
                for ts, val in zip(timestamps, values):
                    if val is not None:
                        # Convert timestamp to human-readable datetime
                        readable_time = datetime.fromtimestamp(ts / 1000.0)
                        if time_based:
                            print(f"Timestamp: {readable_time} | Value: {val/1000000}")
                        else:
                            print(f"Timestamp: {readable_time} | Value: {val}")

                    else:
                        readable_time = datetime.fromtimestamp(ts / 1000.0)
                        print(f"Timestamp: {readable_time} | Value: None")
                    
                    # Collect data for CSV
                    value_in_seconds = val / 1000 if val is not None else None
                    csv_data.append([readable_time, value_in_seconds])

            
            # Write to CSV file
            with open('output_files/BrowserMonitorMetric.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Timestamp', 'Value'])
                writer.writerows(csv_data)







# -- Singleton access --
_client = None

def get_dynatrace_client():
    global _client

    if _client is None:
        config = get_config()
        load_dotenv()
        _client = DynatraceClient(os.getenv("DYNATRACE_API_TOKEN"), os.getenv("DYNATRACE_URL"))
    return _client
