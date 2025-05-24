import requests
import datetime
import pandas as pd

# Parámetros para llamar a los servicios


ENV_ID = 'kae68552'
SERVICE_ID = 'SERVICE-FD9343224D905203'

# Endpoint de la API de Dynatrace
url = f'https://{ENV_ID}.live.dynatrace.com/api/v2/metrics/query'

# Encabezados para la llamada
headers = {
    'Authorization': f'Api-Token {API_TOKEN}'
}

# Parámetros para la llamada
params = {
    'metricSelector': 'builtin:service.response.time',
    'resolution': '1m',
    'entitySelector': f'entityId({SERVICE_ID})',
    'from': 'now-7d',
    'to': 'now'
}

response = requests.get(url, headers=headers, params=params)
data = response.json()

print("Entregando información de consultas sobre el servicio ComercioTransaccionesController")


# Navigate to the time series data
series = data['result'][0]['data'][0]
timestamps = series['timestamps']
values = series['values']

# Para archivo de texto y salida en pantalla. Podría unirse con el bloque anterior
# Por ahora está así para una solución rápida
with open('response_times.txt', 'w') as f:
    f.write(f"Entregando información de consultas sobre el servicio ComercioTransaccionesController\n\n")
    for ts, val in zip(timestamps, values):
        if val is not None:
            time_str = datetime.datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M:%S')
            ms = val / 1000  # convert microseconds → milliseconds
            print(f"{time_str}: {ms:.2f} ms")
            f.write(f"{time_str}: {ms:.2f} ms\n")
    f.write(f"\nFin de los datos")

# Prepare the data
# Esto es para generar el Excel
# Podemos generar estadísticas en Excel
rows = []
for ts, val in zip(timestamps, values):
    if val is not None:
        time_str = datetime.datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M:%S')
        ms = val / 1000  # convert microseconds to milliseconds
        threshold = 1 if ms < 3000 else 0
        rows.append({
            "Timestamp": time_str,
            "Response time": round(ms, 2),
            "Threshold": threshold
        })

# Create a DataFrame
df = pd.DataFrame(rows)

# Export to Excel
df.to_excel("Tiempos de respuesta.xlsx", index=False, sheet_name="ComercioTransaccionesController")

with pd.ExcelWriter("Tiempos de respuesta.xlsx", engine="openpyxl") as writer:
    # First sheet with raw data
    df.to_excel(writer, index=False, sheet_name="ComercioTransaccionesController")

    # Calculate statistics
    avg_response = df["Response time"].mean()
    min_response = df["Response time"].min()
    max_response = df["Response time"].max()
    median_response = df["Response time"].median()
    total_count = len(df)
    above_threshold_pct = (df["Threshold"] == 0).sum() / total_count * 100
    below_threshold_pct = (df["Threshold"] == 1).sum() / total_count * 100

    # Create stats DataFrame
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

    # Second sheet with stats
    stats_df.to_excel(writer, index=False, sheet_name="Stats")

    # Convert timestamps to datetime and extract the date
    df["Date"] = pd.to_datetime(df["Timestamp"]).dt.date

    # Group by date and compute daily stats
    daily_stats_df = df.groupby("Date").agg({
        "Response time": ["mean", "min", "max", "median", lambda x: (x >= 3000).mean() * 100, lambda x: (x < 3000).mean() * 100]
    })

    # Flatten the column names
    daily_stats_df.columns = [
        "Average response time",
        "Fastest response time",
        "Slowest response time",
        "Median response time",
        "Percent above threshold (>= 3000 ms)",
        "Percent below threshold (< 3000 ms)"
    ]

    # Reset index so 'Date' becomes a column
    daily_stats_df = daily_stats_df.reset_index()

    # Optional: round values for clarity
    daily_stats_df = daily_stats_df.round(2)

    # Write to third sheet 
    daily_stats_df.to_excel(writer, index=False, sheet_name="Daily averages")

    df["Date"] = pd.to_datetime(df["Timestamp"]).dt.date
    df["Hour"] = pd.to_datetime(df["Timestamp"]).dt.hour

    pivot_df = df.groupby(["Date", "Hour"]).agg(
        total=("Threshold", "count"),
        under_threshold=("Threshold", "sum")  # since 1 means under
    ).reset_index()

    pivot_df["over_threshold"] = pivot_df["total"] - pivot_df["under_threshold"]
    pivot_df["% under"] = (pivot_df["under_threshold"] / pivot_df["total"]) * 100
    pivot_df["% over"] = 100 - pivot_df["% under"]

    pivot_df.to_excel(writer, sheet_name="Pivot", index=False)


