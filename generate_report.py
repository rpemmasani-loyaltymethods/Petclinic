import json
import os

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_quality_gate_status(quality_data):
    try:
        return quality_data['projectStatus']['status']
    except Exception:
        return "Unknown"

def extract_metrics(metrics_data):
    metrics = {}
    try:
        for measure in metrics_data['component']['measures']:
            metrics[measure['metric']] = float(measure['value'])
    except Exception:
        pass
    return metrics

def generate_combined_html(quality_status, metrics):
    covered_lines = int(metrics.get("lines_to_cover", 0) - metrics.get("uncovered_lines", 0))
    total_lines = int(metrics.get("lines_to_cover", 0))
    coverage_percent = metrics.get("coverage", 0.0)

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Combined SonarQube Report</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 20px;
    }}
    .bar-container {{
      background:#ddd;
      width:400px;
      margin-bottom:10px;
    }}
    .bar-fill {{
      height:20px;
      color:white;
      text-align:center;
      line-height: 20px;
    }}
    .metric-label {{
      font-weight: bold;
    }}
    table {{
      border-collapse: collapse;
      margin-top: 20px;
    }}
    th, td {{
      border: 1px solid #999;
      padding: 8px 12px;
      text-align: left;
    }}
    h2 {{
      margin-top: 30px;
    }}
  </style>
</head>
<body>

  <h1>SonarQube Combined Coverage & Metrics Report</h1>

  <h2>Quality Gate Status:
    <span style="color:{'green' if quality_status == 'OK' else 'red'};">
      {quality_status}
    </span>
  </h2>

  <h2>Code Coverage - {coverage_percent:.1f}% ({covered_lines}/{total_lines} elements)</h2>

  <div class="metric-label">Methods</div>
  <div class="bar-container">
    <div class="bar-fill" style="width:{metrics.get('functions', 0)}%; background:green;">{int(metrics.get('method_coverage', 0))}%</div>
  </div>

  <div class="metric-label">Conditionals (Branches)</div>
  <div class="bar-container">
    <div class="bar-fill" style="width:{metrics.get('branch_coverage', 0)}%; background:green;">{int(metrics.get('branch_coverage', 0))}%</div>
  </div>

  <div class="metric-label">Statements (Lines)</div>
  <div class="bar-container">
    <div class="bar-fill" style="width:{metrics.get('line_coverage', 0)}%; background:green;">{int(metrics.get('line_coverage', 0))}%</div>
  </div>

  <h2>SonarQube Metrics</h2>
  <table border="1" cellpadding="5">
    <tr><th>Metric</th><th>Value</th></tr>
    <tr><td>Lines of Code</td><td>{int(metrics.get("ncloc", 0))}</td></tr>
    <tr><td>Statements</td><td>{int(metrics.get("statements", 0))}</td></tr>
    <tr><td>Complexity</td><td>{int(metrics.get("complexity", 0))}</td></tr>
    <tr><td>Violations</td><td>{int(metrics.get("violations", 0))}</td></tr>
    <tr><td>Coverage</td><td>{float(metrics.get("coverage", 0)):.1f}%</td></tr>
    <tr><td>Line Coverage</td><td>{float(metrics.get("line_coverage", 0)):.1f}%</td></tr>
    <tr><td>Branch Coverage</td><td>{float(metrics.get("branch_coverage", 0)):.1f}%</td></tr>
    <tr><td>Code Smells</td><td>{int(metrics.get("code_smells", 0))}</td></tr>
    <tr><td>Bugs</td><td>{int(metrics.get("bugs", 0))}</td></tr>
    <tr><td>Vulnerabilities</td><td>{int(metrics.get("vulnerabilities", 0))}</td></tr>
    <tr><td>Security Hotspots</td><td>{int(metrics.get("security_hotspots", 0))}</td></tr>
    <tr><td>Duplicated Lines</td><td>{int(metrics.get("duplicated_lines", 0))}</td></tr>
    <tr><td>Functions</td><td>{int(metrics.get("functions", 0))}</td></tr>
    <tr><td>Lines to Cover</td><td>{int(metrics.get("lines_to_cover", 0))}</td></tr>
    <tr><td>Conditions to Cover</td><td>{int(metrics.get("conditions_to_cover", 0))}</td></tr>
    <tr><td>Tests</td><td>{int(metrics.get("tests", 0))}</td></tr>
    <tr><td>Alert Status</td><td>{metrics.get("alert_status", "N/A")}</td></tr>
  </table>
  
</body>
</html>
"""

def main():
    quality_file = os.path.join('archive', 'sonar_quality.json')
    metrics_file = os.path.join('archive', 'sonar_metrics.json')
    combined_report = os.path.join('archive', 'combined_metrics_report.html')

    try:
        quality_data = load_json(quality_file)
        metrics_data = load_json(metrics_file)
    except Exception as e:
        print(f"[ERROR] Failed to load JSON files: {e}")
        return

    quality_status = extract_quality_gate_status(quality_data)
    metrics = extract_metrics(metrics_data)

    try:
        with open(combined_report, 'w', encoding='utf-8') as f:
            f.write(generate_combined_html(quality_status, metrics))
        print(f"[INFO] ✅ combined_metrics_report.html written successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to write combined report: {e}")

if __name__ == "__main__":
    main()