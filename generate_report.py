import json
from pathlib import Path

# Load JSON files
try:
    with open("sonar_quality.json", "r") as f:
        quality_data = json.load(f)
    with open("sonar_metrics.json", "r") as f:
        metrics_data = json.load(f)
except Exception as e:
    print(f"[ERROR] Failed to load JSON files: {e}")
    exit(1)

# Extract relevant data
project_status = quality_data.get("projectStatus", {}).get("status", "UNKNOWN")

metrics = {}
for m in metrics_data.get("component", {}).get("measures", []):
    metrics[m["metric"]] = m["value"]

# Prepare inline styles
style = """
<style>
body {
    font-family: Arial, sans-serif;
    margin: 20px;
}
h1 {
    color: #2c3e50;
}
table {
    border-collapse: collapse;
    width: 60%;
    margin-top: 20px;
}
th, td {
    text-align: left;
    padding: 10px;
    border-bottom: 1px solid #ddd;
}
th {
    background-color: #f2f2f2;
}
.status-ok {
    color: green;
    font-weight: bold;
}
.status-failed {
    color: red;
    font-weight: bold;
}
</style>
"""

# Build HTML content
html_content = f"""
<html>
<head>
    <title>SonarQube Metrics Report</title>
    {style}
</head>
<body>
    <h1>SonarQube Metrics Report</h1>
    <p><strong>Quality Gate Status:</strong> <span class="{ 'status-ok' if project_status == 'OK' else 'status-failed' }">{project_status}</span></p>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Lines of Code (ncloc)</td><td>{metrics.get('ncloc', 'N/A')}</td></tr>
        <tr><td>Complexity</td><td>{metrics.get('complexity', 'N/A')}</td></tr>
        <tr><td>Violations</td><td>{metrics.get('violations', 'N/A')}</td></tr>
        <tr><td>Coverage (%)</td><td>{metrics.get('coverage', 'N/A')}</td></tr>
        <tr><td>Code Smells</td><td>{metrics.get('code_smells', 'N/A')}</td></tr>
    </table>
</body>
</html>
"""

# Save to HTML file
output_dir = Path("archive")
output_dir.mkdir(exist_ok=True)
with open(output_dir / "metrics_report.html", "w") as f:
    f.write(html_content)

print("[INFO] metrics_report.html successfully generated.")
