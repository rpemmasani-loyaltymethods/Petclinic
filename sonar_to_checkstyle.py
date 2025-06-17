import json
import xml.etree.ElementTree as ET
import os

def main():
    input_file = os.path.join('archive', 'sonar_issues.json')
    output_file = os.path.join('archive', 'sonar_checkstyle.xml')

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    issues = data.get('issues', [])

    checkstyle = ET.Element('checkstyle', version="8.0")
    files = {}

    for issue in issues:
        # SonarQube 'component' is usually 'project:path/to/file'
        component = issue.get('component', 'unknown')
        file_path = component.split(':', 1)[-1] if ':' in component else component
        line = str(issue.get('line', 1))
        message = issue.get('message', '')
        severity = issue.get('severity', 'INFO').lower()
        rule = issue.get('rule', 'sonarqube')

        if file_path not in files:
            files[file_path] = ET.SubElement(checkstyle, 'file', name=file_path)
        ET.SubElement(
            files[file_path], 'error',
            line=line,
            severity=severity,
            message=message,
            source=rule
        )

    tree = ET.ElementTree(checkstyle)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"Checkstyle XML written to {output_file}")

if __name__ == "__main__":
    main()