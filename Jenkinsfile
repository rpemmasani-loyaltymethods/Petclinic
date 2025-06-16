pipeline {
    agent any

    parameters {
        string(name: 'SONAR_PROJECT_KEY', description: 'SonarQube project key')
        string(name: 'SONAR_PROJECT_NAME', description: 'SonarQube project name')
        choice(name: 'QUALITY_GATE', choices: ['Sonar way', 'Default-Quality-Gate', 'Main-Quality-Gate', 'Feature-Quality-Gate'], description: 'Select the quality gate')
    }

    environment {
        SONARQUBE_SERVER = 'Sonarqube-8.9.2'
        MAVEN_HOME = tool name: 'maven3'
        SONARQUBE_URL = "https://sonarqube.devops.lmvi.net/"
        SONARQUBE_TOKEN = credentials('SONARQUBE_TOKEN')
    }

    stages {
        stage('Git Checkout') {
            steps {
                git branch: "${env.BRANCH_NAME}", url: 'https://github.com/rpemmasani-loyaltymethods/Petclinic.git'
                echo "Checked out branch: ${env.BRANCH_NAME}"
            }
        }

        stage('Build & Test') {
            steps {
                script {
                    if (fileExists('mvnw')) {
                        sh '''
                            chmod +x ./mvnw
                            ./mvnw clean verify
                        '''
                    } else {
                        sh "${MAVEN_HOME}/bin/mvn clean verify"
                    }
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def projectKey = params.SONAR_PROJECT_KEY
                    def projectName = params.SONAR_PROJECT_NAME
                    def qualityGate = params.QUALITY_GATE

                    withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                        sh """
                            ${MAVEN_HOME}/bin/mvn sonar:sonar \
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

                    echo '⏳ Waiting for analysis to complete...'
                    sleep(time: 2, unit: 'MINUTES')
                }
            }
        }

        stage('Quality Gate Check') {
            steps {
                script {
                    def statusUrl = "${SONARQUBE_URL}api/qualitygates/project_status?projectKey=${params.SONAR_PROJECT_KEY}"

                    withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                        sh """
                            curl -s -u ${SONARQUBE_TOKEN}: ${statusUrl} -o sonar_status.json
                        """
                    }

                    def sonarJson = readFile('sonar_status.json')
                    def sonarData = new groovy.json.JsonSlurper().parseText(sonarJson)
                    echo "SonarQube Response Json: ${sonarData}"

                    def gateStatus = sonarData?.projectStatus?.status ?: 'UNKNOWN'
                    echo "🔍 Quality Gate Status: ${gateStatus}"

                    if (gateStatus != 'OK') {
                        error "❌ Quality Gate Failed!"
                    }
                }
            }
        }

        stage('Generate Graphical HTML Report') {
            steps {
                script {
                    writeFile file: 'generate_report.py', text: '''
import json, os

try:
    with open("sonar_status.json") as f:
        data = json.load(f)
except Exception as e:
    print("[ERROR] Failed to load JSON:", e)
    exit(1)

html = '''
<!DOCTYPE html>
<html>
<head>
    <title>SonarQube Quality Gate Report</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        h1 { color: #2E8B57; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; border: 1px solid #ddd; }
        th { background: #f4f4f4; }
        tr:nth-child(even) { background-color: #f9f9f9; }
    </style>
</head>
<body>
'''

status = data.get("projectStatus", {}).get("status", "UNKNOWN")
html += f"<h1>Quality Gate Status: {status}</h1><table><tr><th>Metric</th><th>Actual Value</th><th>Status</th><th>Error Threshold</th></tr>"

for cond in data.get("projectStatus", {}).get("conditions", []):
    html += f"<tr><td>{cond.get('metricKey')}</td><td>{cond.get('actualValue')}</td><td>{cond.get('status')}</td><td>{cond.get('errorThreshold')}</td></tr>"

html += "</table></body></html>"

os.makedirs("archive", exist_ok=True)
with open("archive/quality_gate_report.html", "w") as f:
    f.write(html)

print("[INFO] Report generated.")
'''

                    // Run the Python script
                    sh 'python3 generate_report.py'
                }
            }
        }
    }

    post {
        always {
            script {
                if (fileExists('archive/quality_gate_report.html')) {
                    publishHTML([
                        reportName: "SonarQube Quality Gate Report",
                        reportDir: 'archive',
                        reportFiles: 'quality_gate_report.html',
                        keepAll: true,
                        allowMissing: false,
                        alwaysLinkToLastBuild: true
                    ])
                } else {
                    echo '⚠️ Skipping HTML publish — report not found.'
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
