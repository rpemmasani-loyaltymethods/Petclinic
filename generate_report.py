import json
import os
from xml.etree.ElementTree import Element, SubElement, ElementTree

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
            key = measure['metric']
            value = measure['value']
            try:
                metrics[key] = float(value)
            except ValueError:
                metrics[key] = value
    except Exception as e:
        print(f"[WARN] Failed to extract metrics: {e}")
    return metrics

def generate_combined_html(quality_status, metrics):
    lines_to_cover = int(metrics.get("lines_to_cover", 0))
    uncovered_lines = int(metrics.get("uncovered_lines", 0))
    covered_lines = lines_to_cover - uncovered_lines
    coverage_percent = float(metrics.get("coverage", 0.0))
    branch_coverage = float(metrics.get("branch_coverage", 0.0))
    line_coverage = float(metrics.get("line_coverage", 0.0))

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

  <h2>Code Coverage - {coverage_percent:.1f}% ({covered_lines}/{lines_to_cover} elements)</h2>

  <div class="metric-label">Conditionals (Branches)</div>
  <div class="bar-container" style="width:300px; height:24px; background:#eee; display:flex;">
    <div style="width:{branch_coverage}%; background:limegreen; text-align:right; color:#222; font-weight:bold;">
      {branch_coverage:.1f}%
    </div>
    <div style="width:{100 - branch_coverage}%; background:#c00;"></div>
  </div>

  <div class="metric-label">Statements (Lines)</div>
  <div class="bar-container" style="width:300px; height:24px; background:#eee; display:flex;">
    <div style="width:{line_coverage}%; background:limegreen; text-align:right; color:#222; font-weight:bold;">
      {line_coverage:.1f}%
    </div>
    <div style="width:{100 - line_coverage}%; background:#c00;"></div>
  </div>

  <h2>SonarQube Metrics</h2>
  <table border="1" cellpadding="5">
    <tr><th>Metric</th><th>Value</th></tr>
    <tr><td>Lines of Code</td><td>{int(metrics.get("ncloc", 0))}</td></tr>
    <tr><td>Statements</td><td>{int(metrics.get("statements", 0))}</td></tr>
    <tr><td>Complexity</td><td>{int(metrics.get("complexity", 0))}</td></tr>
    <tr><td>Violations</td><td>{int(metrics.get("violations", 0))}</td></tr>
    <tr><td>Coverage</td><td>{coverage_percent:.1f}%</td></tr>
    <tr><td>Line Coverage</td><td>{line_coverage:.1f}%</td></tr>
    <tr><td>Branch Coverage</td><td>{branch_coverage:.1f}%</td></tr>
    <tr><td>Code Smells</td><td>{int(metrics.get("code_smells", 0))}</td></tr>
    <tr><td>Bugs</td><td>{int(metrics.get("bugs", 0))}</td></tr>
    <tr><td>Vulnerabilities</td><td>{int(metrics.get("vulnerabilities", 0))}</td></tr>
    <tr><td>Security Hotspots</td><td>{int(metrics.get("security_hotspots", 0))}</td></tr>
    <tr><td>Duplicated Lines</td><td>{int(metrics.get("duplicated_lines", 0))}</td></tr>
    <tr><td>Methods</td><td>{int(metrics.get("functions", 0))}</td></tr>
    <tr><td>Lines to Cover</td><td>{lines_to_cover}</td></tr>
    <tr><td>Conditions to Cover</td><td>{int(metrics.get("conditions_to_cover", 0))}</td></tr>
    <tr><td>Tests</td><td>{int(metrics.get("tests", 0))}</td></tr>
    <tr><td>Alert Status</td><td>{metrics.get("alert_status", "N/A")}</td></tr>
  </table>

</body>
</html>
"""

def generate_cobertura_xml(metrics, output_path='coverage/sonarqube_cobertura.xml'):
    lines_to_cover = int(metrics.get("lines_to_cover", 0))
    uncovered_lines = int(metrics.get("uncovered_lines", 0))
    covered_lines = lines_to_cover - uncovered_lines
    line_coverage_percent = float(metrics.get("line_coverage", 0.0))
    branch_coverage_percent = float(metrics.get("branch_coverage", 0.0))
    conditions_to_cover = int(metrics.get("conditions_to_cover", 0))
    branches_covered = int(conditions_to_cover * (branch_coverage_percent / 100)) if conditions_to_cover > 0 else 0

    coverage_elem = Element("coverage", {
        "line-rate": f"{line_coverage_percent / 100:.4f}",
        "branch-rate": f"{branch_coverage_percent / 100:.4f}",
        "lines-covered": str(covered_lines),
        "lines-valid": str(lines_to_cover),
        "branches-covered": str(branches_covered),
        "branches-valid": str(conditions_to_cover),
        "complexity": str(metrics.get("complexity", 0)),
        "timestamp": "0",
        "version": "1.9"
    })

    sources = SubElement(coverage_elem, "sources")
    SubElement(sources, "source").text = "/jenkins/workspace/SonarPetClinic_main/src/main/java"

    packages = SubElement(coverage_elem, "packages")
    package = SubElement(packages, "package", {
        "name": "org.springframework.samples.petclinic",
        "line-rate": f"{line_coverage_percent / 100:.4f}",
        "branch-rate": f"{branch_coverage_percent / 100:.4f}",
        "complexity": "0"
    })

    classes = SubElement(package, "classes")
    cls = SubElement(classes, "class", {
        "name": "PetclinicInitializer",
        "filename": "org/springframework/samples/petclinic/PetclinicInitializer.java",
        "line-rate": f"{line_coverage_percent / 100:.4f}",
        "branch-rate": f"{branch_coverage_percent / 100:.4f}",
        "complexity": "0"
    })

    lines = SubElement(cls, "lines")
    for i in range(1, lines_to_cover + 1):
        hit = "1" if i <= covered_lines else "0"
        SubElement(lines, "line", {
            "number": str(i),
            "hits": hit,
            "branch": "false"
        })

    if conditions_to_cover > 0:
        SubElement(lines, "line", {
            "number": str(lines_to_cover + 1),
            "hits": "1",
            "branch": "true",
            "condition-coverage": f"{branch_coverage_percent:.1f}% ({branches_covered}/{conditions_to_cover})"
        })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    ElementTree(coverage_elem).write(output_path, encoding="utf-8", xml_declaration=True)
    print(f"[INFO] ✅ Cobertura XML written to: {output_path}")


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

    try:
        generate_cobertura_xml(metrics)
    except Exception as e:
        print(f"[ERROR] Failed to write Cobertura XML: {e}")

if __name__ == "__main__":
    main()
