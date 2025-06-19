import json
import xml.etree.ElementTree as ET

def generate_cobertura_xml(metrics_file, output_file):
    with open(metrics_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    measures = {m["metric"]: float(m["value"]) for m in data["component"]["measures"] if "value" in m}

    total_lines = int(measures.get("lines_to_cover", 0))
    uncovered_lines = int(measures.get("uncovered_lines", 0))
    covered_lines = total_lines - uncovered_lines
    line_rate = covered_lines / total_lines if total_lines > 0 else 0.0

    # Create XML structure (mimicking Cobertura's format)
    coverage = ET.Element("coverage", {
        "line-rate": f"{line_rate:.4f}",
        "branch-rate": f"{measures.get('branch_coverage', 0)/100:.4f}",
        "lines-covered": str(covered_lines),
        "lines-valid": str(total_lines),
        "branches-covered": "0",
        "branches-valid": "0",
        "complexity": str(measures.get("complexity", 0)),
        "timestamp": "0",
        "version": "1.9"
    })

    sources = ET.SubElement(coverage, "sources")
    ET.SubElement(sources, "source").text = "."

    packages = ET.SubElement(coverage, "packages")
    package = ET.SubElement(packages, "package", {
        "name": "sonarqube",
        "line-rate": f"{line_rate:.4f}",
        "branch-rate": "0.0",
        "complexity": str(measures.get("complexity", 0))
    })

    classes = ET.SubElement(package, "classes")
    class_ = ET.SubElement(classes, "class", {
        "name": "sonar_metrics_summary",
        "filename": "summary",
        "line-rate": f"{line_rate:.4f}",
        "branch-rate": "0.0",
        "complexity": str(measures.get("complexity", 0))
    })

    lines = ET.SubElement(class_, "lines")
    for i in range(1, total_lines + 1):
        hit = "1" if i <= covered_lines else "0"
        ET.SubElement(lines, "line", {
            "number": str(i),
            "hits": hit,
            "branch": "false"
        })

    # Write to output file
    tree = ET.ElementTree(coverage)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"[✅] Cobertura XML report generated: {output_file}")

if __name__ == "__main__":
    generate_cobertura_xml("archive/sonar_metrics.json", "archive/sonar_cobertura.xml")
