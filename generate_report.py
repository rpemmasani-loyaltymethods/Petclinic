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

def generate_html_report(quality_status, metrics):
    html = f"""
    <html>
    <head>
        <title>SonarQube Metrics Report</title>
    </head>
    <body>
        <h1>SonarQube Metrics Report</h1>
        <h2>Quality Gate Status: <span>{quality_status}</span></h2>
        <h2>Metrics</h2>
        <table border="1" cellpadding="8" cellspacing="0">
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr><td>Lines of Code</td><td>{metrics.get('ncloc', 'N/A')}</td></tr>
            <tr><td>Complexity</td><td>{metrics.get('complexity', 'N/A')}</td></tr>
            <tr><td>Violations</td><td>{metrics.get('violations', 'N/A')}</td></tr>
            <tr><td>Coverage</td><td>{metrics.get('coverage', 'N/A')}</td></tr>
            <tr><td>Code Smells</td><td>{metrics.get('code_smells', 'N/A')}</td></tr>
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