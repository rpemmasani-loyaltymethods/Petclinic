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
        SONARQUBE_TOKEN = credentials('SONARQUBE_TOKEN')
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

        stage('Quality Gate') {
            steps {
                script {
                    def sonarUrl = "${SONARQUBE_URL}api/qualitygates/project_status?projectKey=${params.SONAR_PROJECT_KEY}"

                    withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                        sh """
                        curl -s -u ${SONARQUBE_TOKEN}: ${sonarUrl} > sonar_status.json
                        """
                        def sonarStatusJson = readFile('sonar_status.json')
                        def sonarData = new groovy.json.JsonSlurper().parseText(sonarStatusJson)
                        echo "SonarQube Response Json: ${sonarData}"
                        def sonarStatus = sonarData?.projectStatus?.status ?: 'Unknown'
                        echo "SonarQube Quality Gate Status: ${sonarStatus}"

                        if (sonarStatus != 'OK') {
                            echo "Quality Gate failed! SonarQube status: ${sonarStatus}"
                            currentBuild.result = 'FAILURE'
                            error "Quality Gate Failed!"
                        }
                    }
                }
            }
        }

        stage('Publish Test Results') {
            steps {
                junit 'target/surefire-reports/*.xml'
            }
        }

        stage('Publish Code Coverage') {
            steps {
                jacoco execPattern: 'target/jacoco.exec', classPattern: 'target/classes', sourcePattern: 'src/main/java', exclusionPattern: ''
            }
        }

        stage('Publish Checkstyle Report') {
            steps {
                recordIssues tools: [checkStyle(pattern: 'target/checkstyle-result.xml')]
            }
        }

        stage('Fetch and Generate Graphical Metrics Report') {
            steps {
                script {
                    def metricsUrl = "${SONARQUBE_URL}api/measures/component?component=${params.SONAR_PROJECT_KEY}&metricKeys=ncloc,complexity,violations,coverage,code_smells,security_hotspots,bugs,vulnerabilities,tests,duplicated_lines,alert_status"

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

metrics = {m['metric']: m.get('value', 'N/A') for m in data['component']['measures']}

html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>SonarQube Metrics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial; padding: 20px; }}
        h1 {{ text-align: center; }}
        .chart-container {{ width: 80%; margin: auto; }}
    </style>
</head>
<body>
    <h1>SonarQube Metrics Dashboard</h1>

    <div class="chart-container">
        <canvas id="metricChart"></canvas>
    </div>

    <script>
        const data = {{
            labels: {list(metrics.keys())},
            datasets: [{{
                label: 'Metric Values',
                data: {[float(metrics[m]) if metrics[m].replace('.', '', 1).isdigit() else 0 for m in metrics]},
                backgroundColor: [
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(255, 206, 86, 0.6)',
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(153, 102, 255, 0.6)',
                    'rgba(255, 159, 64, 0.6)',
                    'rgba(199, 199, 199, 0.6)',
                    'rgba(83, 102, 255, 0.6)',
                    'rgba(255, 122, 64, 0.6)',
                    'rgba(100, 199, 99, 0.6)',
                    'rgba(255, 205, 86, 0.6)',
                ]
            }}]
        }};

        const config = {{
            type: 'bar',
            data: data,
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ display: false }},
                    title: {{
                        display: true,
                        text: 'SonarQube Project Metrics'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }};

        new Chart(document.getElementById('metricChart'), config);
    </script>
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
