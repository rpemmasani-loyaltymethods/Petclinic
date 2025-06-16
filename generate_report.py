import json
import os

quality_path = 'archive/sonar_quality.json'
metrics_path = 'archive/sonar_metrics.json'
output_path = 'archive/metrics_report.html'

try:
    with open(quality_path, 'r') as f:
        quality_data = json.load(f)

    with open(metrics_path, 'r') as f:
        metrics_data = json.load(f)

except Exception as e:
    print(f"[ERROR] Failed to load JSON files: {e}")
    exit(1)

# Extract quality gate status
project_status = quality_data.get('projectStatus', {})
quality_gate_status = project_status.get('status', 'Unknown')
conditions = project_status.get('conditions', [])

# Extract metrics
component = metrics_data.get('component', {})
measures = component.get('measures', [])

metric_map = {m['metric']: m['value'] for m in measures}

# Create HTML
html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SonarQube Metrics Dashboard</title>
    <style>
        body {{
            margin: 0;
            font-family: 'Segoe UI', sans-serif;
            background-color: #f4f6f8;
            color: #333;
        }}
        .sidebar {{
            width: 250px;
            background-color: #0d47a1;
            height: 100vh;
            position: fixed;
            padding: 30px 20px;
            color: white;
        }}
        .sidebar h2 {{
            color: #fff;
            font-size: 22px;
            margin-bottom: 20px;
        }}
        .sidebar .metric {{
            margin-bottom: 15px;
        }}
        .sidebar .metric span {{
            display: block;
            font-size: 14px;
            color: #bbdefb;
        }}
        .sidebar .metric .value {{
            font-size: 18px;
            color: #ffffff;
            font-weight: bold;
        }}
        .main {{
            margin-left: 270px;
            padding: 30px;
        }}
        .status {{
            font-size: 20px;
            font-weight: bold;
            color: {'green' if quality_gate_status == 'OK' else 'red'};
        }}
        .condition {{
            margin-bottom: 10px;
            font-size: 15px;
        }}
    </style>
</head>
<body>

<div class="sidebar">
    <h2>SonarQube Metrics</h2>
    <div class="metric"><span>Lines of Code</span><div class="value">{metric_map.get('ncloc', 'N/A')}</div></div>
    <div class="metric"><span>Complexity</span><div class="value">{metric_map.get('complexity', 'N/A')}</div></div>
    <div class="metric"><span>Violations</span><div class="value">{metric_map.get('violations', 'N/A')}</div></div>
    <div class="metric"><span>Coverage</span><div class="value">{metric_map.get('coverage', 'N/A')}%</div></div>
    <div class="metric"><span>Code Smells</span><div class="value">{metric_map.get('code_smells', 'N/A')}</div></div>
</div>

<div class="main">
    <h1>SonarQube Quality Gate Report</h1>
    <p class="status">Quality Gate Status: {quality_gate_status}</p>
    <hr />
    <h3>Conditions:</h3>
"""

# Append condition info
for cond in conditions:
    html += f"""
    <div class="condition">
        <b>{cond.get('metricKey')}</b>: {cond.get('status')} (Actual: {cond.get('actualValue')}, Threshold: {cond.get('errorThreshold')})
    </div>
    """

html += """
</div>
</body>
</html>
"""

# Write report
with open(output_path, 'w') as f:
    f.write(html)

print(f"✅ HTML report generated at {output_path}")
