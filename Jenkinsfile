pipeline {
    agent any

    parameters {
        string(name: 'SONAR_PROJECT_KEY', description: 'Unique identifier')
        string(name: 'SONAR_PROJECT_NAME', description: 'Name of the project')
        choice(name: 'QUALITY_GATE', choices: ['Sonar way', 'Default-Quality-Gate', 'Main-Quality-Gate', 'Feature-Quality-Gate'], description: 'Which quality gate to apply.')
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

        stage('Build & Test') {
            steps {
                script {
                    if (fileExists('mvnw')) {
                        sh """
                        chmod +x ./mvnw
                        ./mvnw clean verify
                        """
                    } else {
                        sh "${MAVEN_HOME}/bin/mvn clean verify"
                    }
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def qualityGate = "${params.QUALITY_GATE}"
                    def projectKey = "${params.SONAR_PROJECT_KEY}"
                    def projectName = "${params.SONAR_PROJECT_NAME}"

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
                        curl --header "Authorization: Basic ${SonarToken}"  \
                          --location "${SONARQUBE_URL}api/qualitygates/select?projectKey=${projectKey}" \
                          --data-urlencode "gateName=${qualityGate}"
                        """
                    }

                    echo 'Sleeping for 2 minutes to allow SonarQube analysis to complete...'
                    sleep(time: 2, unit: 'MINUTES')
                }
            }
        }

        stage('Quality Gate Check') {
            steps {
                script {
                    def sonarUrl = "${SONARQUBE_URL}api/qualitygates/project_status?projectKey=${params.SONAR_PROJECT_KEY}"

                    withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                        sh """
                        HTTP_CODE=\$(curl -s -o metrics.json -w "%{http_code}" -u ${SONARQUBE_TOKEN}: "${sonarUrl}")
                        if [ "\$HTTP_CODE" -ne 200 ]; then
                          echo "Failed to fetch SonarQube quality gate status. HTTP \$HTTP_CODE"
                          cat metrics.json
                          exit 1
                        fi
                        """
                    }

                    def sonarStatusJson = readFile('metrics.json')
                    def sonarData = new groovy.json.JsonSlurper().parseText(sonarStatusJson)
                    def sonarStatus = sonarData?.projectStatus?.status ?: 'Unknown'
                    echo "SonarQube Quality Gate Status: ${sonarStatus}"

                    if (sonarStatus != 'OK') {
                        error "Quality Gate Failed! SonarQube status: ${sonarStatus}"
                    }
                }
            }
        }

        stage('Generate SonarQube HTML Report') {
            steps {
                script {
                    def pythonScript = """
import json

with open('metrics.json', 'r') as f:
    data = json.load(f)

status = data.get('projectStatus', {}).get('status', 'UNKNOWN')

html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>SonarQube Quality Gate Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
        h1 {{ color: #2C3E50; text-align: center; }}
        table {{ width: 80%; margin: 0 auto; border-collapse: collapse; font-size: 14px; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
        th {{ background-color: #f4f4f4; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .ok {{ color: green; font-weight: bold; }}
        .error {{ color: red; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>SonarQube Quality Gate Report</h1>
    <h2 style="text-align: center;">Status: <span class="{{ 'ok' if status == 'OK' else 'error' }}">{{ status }}</span></h2>
    <table>
        <tr><th>Metric</th><th>Status</th><th>Value</th><th>Threshold</th></tr>
'''

for cond in data['projectStatus'].get('conditions', []):
    html_content += f'''
    <tr>
        <td>{cond.get('metricKey')}</td>
        <td class="{{ 'ok' if cond.get('status') == 'OK' else 'error' }}">{cond.get('status')}</td>
        <td>{cond.get('actualValue', 'N/A')}</td>
        <td>{cond.get('errorThreshold', 'N/A')}</td>
    </tr>
'''

html_content += '''
    </table>
</body>
</html>
'''

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
        success {
            echo '✅ Pipeline completed successfully.'
        }
        failure {
            echo '❌ Pipeline failed.'
        }
        always {
            cleanWs()
            publishHTML([
                reportName: "SonarQube Metrics Report ${env.BUILD_NUMBER}",
                reportDir: 'archive',
                reportFiles: 'metrics_report.html',
                keepAll: true,
                allowMissing: false,
                alwaysLinkToLastBuild: true
            ])
        }
    }
}
