import json
import os

try:
    with open('quality_gate.json', 'r') as f:
        data = json.load(f)

    project_status = data.get("projectStatus", {})
    status = project_status.get("status", "UNKNOWN")
    cayc_status = project_status.get("caycStatus", "UNKNOWN")
    period = project_status.get("period", {})
    conditions = project_status.get("conditions", [])

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>SonarQube Quality Gate Report</title>
    <style>
        body {{ font-family: Arial; padding: 20px; }}
        h2 {{ color: #333; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
        th {{ background-color: #f2f2f2; }}
        .status-ok {{ background-color: #4CAF50; color: white; }}
        .status-fail {{ background-color: #f44336; color: white; }}
    </style>
</head>
<body>
    <h2>SonarQube Quality Gate Status</h2>
    <p><strong>Status:</strong> <span class="{ 'status-ok' if status == 'OK' else 'status-fail' }">{status}</span></p>
    <p><strong>Compliance Status:</strong> {cayc_status}</p>
    <p><strong>Evaluated on:</strong> {period.get('date', 'N/A')} (Mode: {period.get('mode', 'N/A')})</p>

    <h3>Conditions</h3>
    <table>
        <tr>
            <th>Metric</th>
            <th>Status</th>
            <th>Actual Value</th>
            <th>Comparator</th>
            <th>Threshold</th>
        </tr>
"""

    for cond in conditions:
        row_class = "status-ok" if cond.get("status") == "OK" else "status-fail"
        html += f"""
        <tr class="{row_class}">
            <td>{cond.get('metricKey')}</td>
            <td>{cond.get('status')}</td>
            <td>{cond.get('actualValue')}</td>
            <td>{cond.get('comparator')}</td>
            <td>{cond.get('errorThreshold')}</td>
        </tr>
"""

    html += """
    </table>
</body>
</html>
"""

    with open("archive/quality_gate_report.html", "w") as f:
        f.write(html)

except Exception as e:
    print(f"[ERROR] Failed to generate report: {e}")
    exit(1)
