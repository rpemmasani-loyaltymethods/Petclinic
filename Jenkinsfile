pipeline {
    agent any

    environment {
        SONAR_PROJECT_KEY = 'Petclinic'
        SONARQUBE_URL = 'https://sonarqube.devops.lmvi.net'
    }

    stages {
        stage('Clone Repository') {
            steps {
                git url: 'https://github.com/spring-projects/spring-petclinic.git'
            }
        }

        stage('Fetch SonarQube Report') {
            steps {
                script {
                    sh '''
                    mkdir -p sonar_report

                    echo "Fetching metrics..."
                    curl -s "${SONARQUBE_URL}/api/measures/component?component=${SONAR_PROJECT_KEY}&metricKeys=ncloc,complexity,violations,coverage,code_smells,bugs,vulnerabilities" -o sonar_report/metrics.json

                    echo "Fetching quality gate..."
                    curl -s "${SONARQUBE_URL}/api/qualitygates/project_status?projectKey=${SONAR_PROJECT_KEY}" -o sonar_report/gate.json
                    '''
                }
            }
        }

        stage('Generate HTML Report') {
            steps {
                script {
                    writeFile file: 'generate_report.py', text: '''
import json
import os

metrics_path = "sonar_report/metrics.json"
gate_path = "sonar_report/gate.json"
output_path = "sonar_report/index.html"

try:
    with open(metrics_path) as f:
        metrics = json.load(f)

    with open(gate_path) as f:
        gate = json.load(f)

    component = metrics["component"]
    metric_map = {item["metric"]: item["value"] for item in component["measures"]}
    quality_gate = gate["projectStatus"]

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SonarQube Quality Report</title>
        <style>
            body {{ font-family: Arial; display: flex; justify-content: space-between; }}
            .metrics, .quality {{ width: 45%; }}
            h2 {{ color: #444; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ padding: 8px; border: 1px solid #ccc; text-align: left; }}
            .status-ok {{ color: green; font-weight: bold; }}
            .status-fail {{ color: red; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="metrics">
            <h2>Metrics</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
    """
    for key, val in metric_map.items():
        html += f"<tr><td>{key}</td><td>{val}</td></tr>"

    html += """
            </table>
        </div>
        <div class="quality">
            <h2>Quality Gate Status</h2>
            <p class="{status_class}">Status: {status}</p>
            <table>
                <tr><th>Metric</th><th>Actual</th><th>Status</th><th>Threshold</th></tr>
    """.format(status=quality_gate["status"],
               status_class="status-ok" if quality_gate["status"] == "OK" else "status-fail")

    for cond in quality_gate["conditions"]:
        html += f"<tr><td>{cond['metricKey']}</td><td>{cond.get('actualValue', '-')}</td><td>{cond['status']}</td><td>{cond.get('errorThreshold', '-')}</td></tr>"

    html += """
            </table>
        </div>
    </body>
    </html>
    """

    os.makedirs("archive", exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html)

    # Copy to archive for Jenkins HTML Publisher
    import shutil
    shutil.copy(output_path, "archive/metrics_report.html")

except Exception as e:
    print(f"[ERROR] Failed to generate report: {e}")
    exit(1)
'''

                    sh 'python3 generate_report.py'
                }
            }
        }

    }

    post {
        always {
            cleanWs()
            script {
                if (fileExists("archive/metrics_report.html")) {
                    publishHTML(target: [
                        reportDir: 'archive',
                        reportFiles: 'metrics_report.html',
                        reportName: 'SonarQube Metrics Report'
                    ])
                } else {
                    echo '⚠️ Skipping publishHTML — metrics_report.html not found.'
                }
            }
        }
    }
}
