pipeline {
    agent any

    parameters {
        string(name: 'SONAR_PROJECT_KEY', description: 'Unique identifier for the project')
        string(name: 'SONAR_PROJECT_NAME', description: 'Project display name')
        choice(name: 'QUALITY_GATE', choices: ['Sonar way', 'Default-Quality-Gate', 'Main-Quality-Gate', 'Feature-Quality-Gate'], description: 'Choose the quality gate')
    }

    environment {
        SONARQUBE_SERVER = 'Sonarqube-8.9.2'
        MAVEN_HOME = tool name: 'maven3'
        SONARQUBE_URL = "https://sonarqube.devops.lmvi.net/"
    }

    stages {

        stage('Git Checkout') {
            steps {
                git branch: "${env.BRANCH_NAME}", changelog: false, poll: false, url: 'https://github.com/rpemmasani-loyaltymethods/Petclinic.git'
                echo "Checked out branch: ${env.BRANCH_NAME}"
            }
        }

        stage('Build & SonarQube Analysis') {
            steps {
                script {
                    def projectKey = "${params.SONAR_PROJECT_KEY}"
                    def projectName = "${params.SONAR_PROJECT_NAME}"
                    def qualityGate = "${params.QUALITY_GATE}"

                    withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                        sh """
                        ${MAVEN_HOME}/bin/mvn clean verify sonar:sonar \
                          -Dsonar.projectKey=${projectKey} \
                          -Dsonar.projectName=${projectName} \
                          -Dsonar.host.url=${SONARQUBE_URL} \
                          -Dsonar.login=${SONARQUBE_TOKEN} \
                          -Dsonar.ws.timeout=600
                        """
                    }

                    withCredentials([string(credentialsId: 'SonarToken', variable: 'SonarToken')]) {
                        sh """
                        curl --header "Authorization: Basic ${SonarToken}" \
                          --location "${SONARQUBE_URL}api/qualitygates/select?projectKey=${projectKey}" \
                          --data-urlencode "gateName=${qualityGate}"
                        """
                    }

                    echo 'Sleeping 2 minutes to allow SonarQube analysis to complete...'
                    sleep(time: 2, unit: 'MINUTES')
                }
            }
        }

        stage('Verify Quality Gate') {
            steps {
                script {
                    def sonarUrl = "${SONARQUBE_URL}api/qualitygates/project_status?projectKey=${params.SONAR_PROJECT_KEY}"

                    withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                        sh "curl -s -u ${SONARQUBE_TOKEN}: ${sonarUrl} > sonar_status.json"
                        def sonarStatusJson = readFile('sonar_status.json')
                        def sonarData = new groovy.json.JsonSlurper().parseText(sonarStatusJson)

                        echo "SonarQube Response JSON: ${sonarData}"
                        def sonarStatus = sonarData?.projectStatus?.status ?: 'Unknown'
                        echo "SonarQube Quality Gate Status: ${sonarStatus}"

                        if (sonarStatus != 'OK') {
                            error "Quality Gate failed: ${sonarStatus}"
                        }
                    }
                }
            }
        }

        stage('Fetch and Generate Graphical Metrics Report') {
            steps {
                script {
                    def metricsUrl = "${SONARQUBE_URL}api/measures/component?component=${params.SONAR_PROJECT_KEY}&metricKeys=ncloc,complexity,violations,coverage,code_smells,security_hotspots,bugs,vulnerabilities,tests,duplicated_lines_density,alert_status"

                    withCredentials([string(credentialsId: 'SonarToken', variable: 'SonarToken')]) {
                        sh """
                        curl --location "${metricsUrl}" \
                          --header "Authorization: Basic ${SonarToken}" > metrics.json
                        """
                    }

                    def pythonScript = """
import json

with open('metrics.json', 'r') as f:
    data = json.load(f)

html_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>SonarQube Metrics Report</title>
    <style>
        body { font-family: Arial; margin: 20px; color: #333; }
        h1 { color: #2C3E50; text-align: center; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; }
        th, td { border: 1px solid #ddd; padding: 8px; }
        th { background-color: #f2f2f2; text-transform: uppercase; }
        tr:nth-child(even) { background-color: #f9f9f9; }
    </style>
</head>
<body>
    <h1>SonarQube Metrics Report</h1>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
'''

for m in data.get("component", {}).get("measures", []):
    html_content += f"<tr><td>{m.get('metric')}</td><td>{m.get('value')}</td></tr>"

html_content += "</table></body></html>"

with open('metrics_report.html', 'w') as f:
    f.write(html_content)
"""
                    writeFile file: 'generate_report.py', text: pythonScript
                    sh 'python3 generate_report.py'
                    sh 'mkdir -p archive && mv metrics_report.html archive/'
                }
            }
        }
    }

    post {
        always {
            script {
                if (fileExists('archive/metrics_report.html')) {
                    publishHTML([
                        reportName: "SonarQube Metrics Report - Build ${env.BUILD_NUMBER}",
                        reportDir: 'archive',
                        reportFiles: 'metrics_report.html',
                        keepAll: true,
                        allowMissing: false,
                        alwaysLinkToLastBuild: true
                    ])
                } else {
                    echo "⚠️ Metrics report not generated."
                }
            }
            cleanWs()
        }
        success {
            echo '✅ Pipeline completed successfully.'
        }
        failure {
            echo '❌ Pipeline failed.'
        }
    }
}
