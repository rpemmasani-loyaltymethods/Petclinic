import json
import os

# Load data
try:
    with open("sonar_quality.json") as f:
        quality_data = json.load(f)

    with open("sonar_metrics.json") as f:
        metrics_data = json.load(f)
except Exception as e:
    print("[ERROR] Failed to load JSON files:", str(e))
    exit(1)

# Prepare output directory
output_dir = "archive"
os.makedirs(output_dir, exist_ok=True)

# Extract quality gate data
status = quality_data.get("projectStatus", {}).get("status", "UNKNOWN")
conditions = quality_data.get("projectStatus", {}).get("conditions", [])

# Extract metrics
measures = metrics_data.get("component", {}).get("measures", [])

# Generate HTML report
with open(f"{output_dir}/metrics_report.html", "w") as f:
    f.write("<html><head><title>SonarQube Report</title></head><body>")
    f.write(f"<h1>Quality Gate Status: {status}</h1>")
    f.write("<table border='1'><tr><th>Metric</th><th>Actual Value</th><th>Status</th><th>Error Threshold</th></tr>")
    for c in conditions:
        f.write(f"<tr><td>{c.get('metricKey')}</td><td>{c.get('actualValue')}</td><td>{c.get('status')}</td><td>{c.get('errorThreshold')}</td></tr>")
    f.write("</table><hr>")

    f.write("<h2>Metrics Overview</h2>")
    for m in measures:
        metric = m.get("metric")
        value = m.get("value", "N/A")
        percent = int(float(value)) if value.replace('.', '', 1).isdigit() else 0
        f.write(f"<div><strong>{metric.capitalize()}</strong>: {value}%<br>")
        f.write(f"<div style='width: 300px; background-color: red;'><div style='width: {percent}%; background-color: green; color: white;'>{percent}%</div></div></div><br>")

    f.write("</body></html>")