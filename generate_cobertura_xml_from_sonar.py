import json
import os
from xml.etree.ElementTree import Element, SubElement, ElementTree

# Load SonarQube metrics from JSON
with open('archive/sonar_metrics.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# ✅ FIXED: Extract numeric measures only
measures = {}
for m in data["component"]["measures"]:
    metric = m.get("metric")
    value = m.get("value")
    try:
        measures[metric] = float(value)
    except (TypeError, ValueError):
        continue  # Skip non-numeric values like "OK"

# Line coverage metrics
lines_to_cover = int(measures.get("lines_to_cover", 0))
uncovered_lines = int(measures.get("uncovered_lines", 0))
covered_lines = lines_to_cover - uncovered_lines
line_coverage_percent = measures.get("line_coverage", 0.0)

# Branch coverage metrics (Conditionals)
conditions_to_cover = int(measures.get("conditions_to_cover", 0))
branch_coverage_percent = measures.get("branch_coverage", 0.0)
branches_covered = int(conditions_to_cover * (branch_coverage_percent / 100)) if conditions_to_cover > 0 else 0

# Root <coverage> tag
coverage_elem = Element("coverage", {
    "line-rate": f"{line_coverage_percent / 100:.4f}",
    "branch-rate": f"{branch_coverage_percent / 100:.4f}",
    "lines-covered": str(covered_lines),
    "lines-valid": str(lines_to_cover),
    "branches-covered": str(branches_covered),
    "branches-valid": str(conditions_to_cover),
    "complexity": str(measures.get("complexity", 0)),
    "timestamp": "0",
    "version": "1.9"
})

# Add <sources>
sources = SubElement(coverage_elem, "sources")
SubElement(sources, "source").text = "."

# Add <packages>
packages = SubElement(coverage_elem, "packages")
package = SubElement(packages, "package", {
    "name": "com.example.sonar",
    "line-rate": f"{line_coverage_percent / 100:.4f}",
    "branch-rate": f"{branch_coverage_percent / 100:.4f}",
    "complexity": "0"
})

# Add <classes>
classes = SubElement(package, "classes")
cls = SubElement(classes, "class", {
    "name": "PetclinicCoverage",
    "filename": "Petclinic.java",
    "line-rate": f"{line_coverage_percent / 100:.4f}",
    "branch-rate": f"{branch_coverage_percent / 100:.4f}",
    "complexity": "0"
})

# Add <lines>
lines = SubElement(cls, "lines")
for i in range(1, lines_to_cover + 1):
    hit = "1" if i <= covered_lines else "0"
    SubElement(lines, "line", {
        "number": str(i),
        "hits": hit,
        "branch": "false"
    })

# Simulated branch coverage line to enable trend graph
if conditions_to_cover > 0:
    SubElement(lines, "line", {
        "number": str(lines_to_cover + 1),
        "hits": "1",
        "branch": "true",
        "condition-coverage": f"{branch_coverage_percent:.1f}% ({branches_covered}/{conditions_to_cover})"
    })

# Write output XML
os.makedirs("coverage", exist_ok=True)
output_path = "coverage/sonarqube_cobertura.xml"
ElementTree(coverage_elem).write(output_path, encoding="utf-8", xml_declaration=True)

print(f"[✅] Cobertura XML written to: {output_path}")