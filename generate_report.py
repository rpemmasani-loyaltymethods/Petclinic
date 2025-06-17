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
            metrics[measure['metric']] = measure['value']
    except Exception:
        pass
    return metrics

def render_progress_bar(label, percent):
    try:
        percent = float(percent)
    except (ValueError, TypeError):
        percent = 0
    green_width = min(max(percent, 0), 100)
    red_width = 100 - green_width
    return f"""
    <tr>
        <td style="font-weight:bold">{label}</td>
        <td style="width:300px">
            <div style="width:100%;background:#eee;height:20px;display:flex;">
                <div style="width:{green_width}%;background:lime;height:20px;"></div>
                <div style="width:{red_width}%;background:#c00;height:20px;"></div>
            </div>
        </td>
        <td style="font-weight:bold">{green_width:.1f}%</td>
    </tr>
    """

def generate_html_report(quality_status, metrics):
    # Use SonarQube metrics keys as available in your JSON
    coverage = metrics.get('coverage', 0)
    code_smells = metrics.get('code_smells', 0)
    violations = metrics.get('violations', 0)
    complexity = metrics.get('complexity', 0)
    ncloc = metrics.get('ncloc', 0)

    html = f"""
    <html>
    <head>
        <title>SonarQube Metrics Report</title>
    </head>
    <body>
        <h1>SonarQube Metrics Report</h1>
        <h2>Quality Gate Status: 
            <span style="color:{'green' if quality_status == 'OK' else 'red'};font-weight:bold;">
                {quality_status}
            </span>
        </h2>
        <h2>Coverage Progress</h2>
        <table>
            {render_progress_bar("Coverage", coverage)}
        </table>
        <h2>Metrics</h2>
        <table border="1" cellpadding="8" cellspacing="0">
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr><td>Lines of Code</td><td>{ncloc}</td></tr>
            <tr><td>Complexity</td><td>{complexity}</td></tr>
            <tr><td>Violations</td><td>{violations}</td></tr>
            <tr><td>Coverage</td><td>{coverage}</td></tr>
            <tr><td>Code Smells</td><td>{code_smells}</td></tr>
        </table>
    </body>
    </html>
    """
    return html

def main():
    quality_file = os.path.join('archive', 'sonar_quality.json')
    metrics_file = os.path.join('archive', 'sonar_metrics.json')
    output_file = os.path.join('archive', 'metrics_report.html')

    try:
        quality_data = load_json(quality_file)
        metrics_data = load_json(metrics_file)
    except Exception as e:
        print(f"[ERROR] Failed to load JSON files: {e}")
        return

    quality_status = extract_quality_gate_status(quality_data)
    metrics = extract_metrics(metrics_data)
    html_report = generate_html_report(quality_status, metrics)

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        print(f"[INFO] Report generated at {output_file}")
    except Exception as e:
        print(f"[ERROR] Failed to write HTML report: {e}")

if __name__ == "__main__":
    main()