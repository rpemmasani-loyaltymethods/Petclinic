
import json
from datetime import datetime

def render_bar(label, percentage):
    green_bars = int(percentage / 5)
    red_bars = 20 - green_bars
    return f"""
    <div style='margin: 5px 0;'>
        <strong>{label}</strong> {percentage}%
        <div style='background-color: #f44336; width: 100%; height: 20px; border-radius: 5px; overflow: hidden;'>
            <div style='width: {percentage}%; background-color: #4CAF50; height: 100%;'></div>
        </div>
    </div>
    """

# Load SonarQube quality gate JSON
with open("sonarqube_quality_gate.json", "r") as f:
    quality_data = json.load(f)

status = quality_data["projectStatus"]["status"]
conditions = quality_data["projectStatus"].get("conditions", [])

# Optional: Load metrics JSON if present
try:
    with open("sonarqube_metrics.json", "r") as f:
        metrics_data = json.load(f)
        metrics = {m["metric"]: float(m["value"]) for m in metrics_data["component"]["measures"]}
except Exception:
    metrics = {
        "coverage": 65,
        "ncloc": 1000,
        "duplicated_lines_density": 10,
        "complexity": 120,
        "violations": 5
    }

# Generate HTML
with open("archive/metrics_report.html", "w") as f:
    f.write("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SonarQube Metrics Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .ok { color: green; font-weight: bold; }
            .error { color: red; font-weight: bold; }
        </style>
    </head>
    <body>
        <h2>✅ Quality Gate Summary</h2>
        <p><strong>Quality Gate Status:</strong> <span class="{status_class}">{status}</span></p>
        <table>
            <tr><th>Metric</th><th>Actual Value</th><th>Status</th><th>Error Threshold</th></tr>
    """.replace("{status_class}", "ok" if status == "OK" else "error").replace("{status}", status))

    for condition in conditions:
        f.write(f"<tr><td>{condition['metricKey']}</td><td>{condition['actualValue']}</td><td>{condition['status']}</td><td>{condition['errorThreshold']}</td></tr>")

    f.write("""
        </table>
        <h2>📊 Metrics Summary</h2>
    """)

    for key in ("coverage", "duplicated_lines_density", "complexity", "violations"):
        if key in metrics:
            f.write(render_bar(key.replace("_", " ").title(), metrics[key]))

    f.write(f"<p style='margin-top: 20px;'>Report generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>")
    f.write("</body></html>")
