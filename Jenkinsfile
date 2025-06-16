pipeline {
    agent any

    parameters {
        string(name: 'SONAR_PROJECT_KEY', description: 'Unique identifier')
        string(name: 'SONAR_PROJECT_NAME', description: 'Name of the project')
        choice(name: 'QUALITY_GATE', choices: ['Sonar way', 'Default-Quality-Gate', 'Main-Quality-Gate', 'Feature-Quality-Gate'], description: 'Quality Gate to apply.')
    }

    environment {
        SONARQUBE_SERVER = 'Sonarqube-8.9.2'
        MAVEN_HOME = tool name: 'maven3'
        SONARQUBE_URL = "https://sonarqube.devops.lmvi.net/"
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: "${env.BRANCH_NAME}", url: 'https://github.com/rpemmasani-loyaltymethods/Petclinic.git'
            }
        }

        stage('Build and SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                    sh """
                        ${MAVEN_HOME}/bin/mvn clean verify sonar:sonar \
                        -Dsonar.projectKey=${params.SONAR_PROJECT_KEY} \
                        -Dsonar.projectName=${params.SONAR_PROJECT_NAME} \
                        -Dsonar.host.url=${SONARQUBE_URL} \
                        -Dsonar.login=${SONARQUBE_TOKEN} \
                        -Dsonar.ws.timeout=600
                    """
                }

                withCredentials([string(credentialsId: 'SonarToken', variable: 'SonarToken')]) {
                    sh """
                        curl --header "Authorization: Basic ${SonarToken}"  \
                        --location "${SONARQUBE_URL}api/qualitygates/select?projectKey=${params.SONAR_PROJECT_KEY}" \
                        --data-urlencode "gateName=${params.QUALITY_GATE}"
                    """
                }

                echo 'Sleeping 2 minutes to allow SonarQube analysis to complete...'
                sleep(time: 2, unit: 'MINUTES')
            }
        }

        stage('Check Quality Gate') {
            steps {
                script {
                    def sonarUrl = "${SONARQUBE_URL}api/qualitygates/project_status?projectKey=${params.SONAR_PROJECT_KEY}"

                    withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                        sh "curl -s -u ${SONARQUBE_TOKEN}: ${sonarUrl} > sonar_status.json"

                        def sonarStatusJson = readFile('sonar_status.json')
                        def sonarData = new groovy.json.JsonSlurper().parseText(sonarStatusJson)
                        echo "SonarQube Response Json: ${sonarData}"

                        def status = sonarData?.projectStatus?.status ?: 'UNKNOWN'
                        echo "SonarQube Quality Gate Status: ${status}"

                        if (status != 'OK') {
                            error "Quality Gate Failed!"
                        }
                    }
                }
            }
        }

        stage('Generate Sonar Metrics Report') {
            steps {
                withCredentials([string(credentialsId: 'SonarToken', variable: 'SonarToken')]) {
                    sh """
                        curl --location "${SONARQUBE_URL}api/measures/component?component=${params.SONAR_PROJECT_KEY}&metricKeys=ncloc,complexity,violations,coverage,code_smells,security_hotspots,bugs,vulnerabilities,tests,duplicated_lines,alert_status" \
                        --header "Authorization: Basic ${SonarToken}" > metrics.json
                    """
                }

                script {
                    def pythonScript = '''
import json, os

try:
    with open("metrics.json", "r") as f:
        data = json.load(f)

    os.makedirs("archive", exist_ok=True)

    html = """
    <!DOCTYPE html><html><head><title>SonarQube Metrics</title><style>
    body { font-family: sans-serif; margin: 20px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ccc; padding: 8px; }
    th { background: #eee; }
    </style></head><body>
    <h2>SonarQube Metrics Report</h2><table>
    <tr><th>Metric</th><th>Value</th></tr>
    """
    for m in data['component']['measures']:
        html += f"<tr><td>{m['metric']}</td><td>{m.get('value', 'N/A')}</td></tr>"
    html += "</table></body></html>"

    with open("archive/metrics_report.html", "w") as f:
        f.write(html)

except Exception as e:
    print(f"[ERROR] Failed to generate report: {e}")
    exit(1)
'''
                    writeFile file: 'generate_report.py', text: pythonScript
                    sh 'python3 generate_report.py'
                }
            }
        }
    }

    post {
        always {
            cleanWs()
            script {
                if (fileExists('archive/metrics_report.html')) {
                    publishHTML([
                        reportName: "SonarQube Metrics Report",
                        reportDir: 'archive',
                        reportFiles: 'metrics_report.html',
                        keepAll: true,
                        alwaysLinkToLastBuild: true
                    ])
                } else {
                    echo "⚠️ Skipping publishHTML — metrics_report.html not found."
                }
            }
        }
        success {
            echo '✅ Pipeline completed successfully.'
        }
        failure {
            echo '❌ Pipeline failed.'
        }
    }
}