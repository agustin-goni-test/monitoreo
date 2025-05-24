import requests
import datetime
import pandas as pd

# --- Configuration ---


ENV_ID = 'kae68552'

# Service name → ID mapping
SERVICE_MAP = {
    "ComercioTransaccionesController": "SERVICE-FD9343224D905203"
}


# --- Functions ---

def get_service_performance(service_id):
    """
    Fetch response time metrics for a given service from Dynatrace.
    """
    url = f'https://{ENV_ID}.live.dynatrace.com/api/v2/metrics/query'
    headers = {
        'Authorization': f'Api-Token {API_TOKEN}'
    }
    params = {
        'metricSelector': 'builtin:service.response.time',
        'resolution': '1m',
        'entitySelector': f'entityId({service_id})',
        'from': 'now-7d',
        'to': 'now'
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def output_to_screen_and_file(service_name, data):
    """
    Output metrics to console and a .txt file.
    """
    series = data['result'][0]['data'][0]
    timestamps = series['timestamps']
    values = series['values']
    
    header = f"Entregando información de consultas sobre el servicio {service_name}"
    print(header)
    
    with open('response_times.txt', 'w', encoding='utf-8') as f:
        f.write(header + "\n\n")
        for ts, val in zip(timestamps, values):
            if val is not None:
                time_str = datetime.datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M:%S')
                ms = val / 1000
                print(f"{time_str}: {ms:.2f} ms")
                f.write(f"{time_str}: {ms:.2f} ms\n")
        f.write("\nFin de los datos\n")


def output_to_excel(service_name, data):
    """
    Create an Excel report with raw data, statistics, daily aggregates, and pivot analysis.
    """
    series = data['result'][0]['data'][0]
    timestamps = series['timestamps']
    values = series['values']

    rows = []
    for ts, val in zip(timestamps, values):
        if val is not None:
            time_str = datetime.datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M:%S')
            ms = val / 1000
            threshold = 1 if ms < 3000 else 0
            rows.append({
                "Timestamp": time_str,
                "Response time": round(ms, 2),
                "Threshold": threshold
            })

    df = pd.DataFrame(rows)

    # Create dynamic filename
    timestamp_suffix = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{service_name}_response_times_{timestamp_suffix}.xlsx"

    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        # Raw data
        df.to_excel(writer, index=False, sheet_name=service_name)

        # Summary stats
        avg_response = df["Response time"].mean()
        min_response = df["Response time"].min()
        max_response = df["Response time"].max()
        median_response = df["Response time"].median()
        total_count = len(df)
        above_threshold_pct = (df["Threshold"] == 0).sum() / total_count * 100
        below_threshold_pct = (df["Threshold"] == 1).sum() / total_count * 100

        stats_df = pd.DataFrame({
            "Metric": [
                "Average response time",
                "Fastest response time",
                "Slowest response time",
                "Median response time",
                "Percent above threshold (>= 3000 ms)",
                "Percent below threshold (< 3000 ms)"
            ],
            "Value": [
                round(avg_response, 2),
                round(min_response, 2),
                round(max_response, 2),
                round(median_response, 2),
                f"{round(above_threshold_pct, 2)}%",
                f"{round(below_threshold_pct, 2)}%"
            ]
        })
        stats_df.to_excel(writer, index=False, sheet_name="Stats")

        # Daily summary
        df["Date"] = pd.to_datetime(df["Timestamp"]).dt.date
        daily_stats_df = df.groupby("Date").agg({
            "Response time": ["mean", "min", "max", "median", lambda x: (x >= 3000).mean() * 100, lambda x: (x < 3000).mean() * 100]
        })
        daily_stats_df.columns = [
            "Average response time",
            "Fastest response time",
            "Slowest response time",
            "Median response time",
            "Percent above threshold (>= 3000 ms)",
            "Percent below threshold (< 3000 ms)"
        ]
        daily_stats_df = daily_stats_df.reset_index().round(2)
        daily_stats_df.to_excel(writer, index=False, sheet_name="Daily averages")

        # Pivot table: by hour
        df["Hour"] = pd.to_datetime(df["Timestamp"]).dt.hour
        pivot_df = df.groupby(["Date", "Hour"]).agg(
            total=("Threshold", "count"),
            under_threshold=("Threshold", "sum")
        ).reset_index()

        pivot_df["over_threshold"] = pivot_df["total"] - pivot_df["under_threshold"]
        pivot_df["% under"] = (pivot_df["under_threshold"] / pivot_df["total"]) * 100
        pivot_df["% over"] = 100 - pivot_df["% under"]

        pivot_df.to_excel(writer, sheet_name="Pivot", index=False)


# --- Entry Point ---

def main():
    for service_name, service_id in SERVICE_MAP.items():
        try:
            data = get_service_performance(service_id)
            output_to_screen_and_file(service_name, data)
            output_to_excel(service_name, data)
        except Exception as e:
            print(f"Error processing service {service_name}: {e}")


if __name__ == "__main__":
    main()
