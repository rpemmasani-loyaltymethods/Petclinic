
pipeline {
    agent any
    environment {
        SONARQUBE_URL = "https://sonarqube.devops.lmvi.net"
        PROJECT_KEY = "Petclinic"
    }
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/rpemmasani-loyaltymethods/Petclinic.git'
            }
        }

        stage('Fetch SonarQube Metrics') {
            steps {
                script {
                    def qualityGateUrl = "${SONARQUBE_URL}/api/qualitygates/project_status?projectKey=${PROJECT_KEY}"
                    def metricsUrl = "${SONARQUBE_URL}/api/measures/component?component=${PROJECT_KEY}&metricKeys=ncloc,complexity,violations,coverage,code_smells,duplicated_lines_density"

                    sh "curl -s '${qualityGateUrl}' -o sonarqube_quality_gate.json"
                    sh "curl -s '${metricsUrl}' -o sonarqube_metrics.json"
                }
            }
        }

        stage('Generate HTML Report') {
            steps {
                script {
                    sh "mkdir -p archive"
                    writeFile file: 'generate_report.py', text: '''${generate_report_py}'''
                    sh 'python3 generate_report.py'
                }
            }
        }
    }

    post {
        always {
            script {
                if (fileExists('archive/metrics_report.html')) {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'archive',
                        reportFiles: 'metrics_report.html',
                        reportName: 'SonarQube Report'
                    ])
                } else {
                    echo "⚠️ Skipping publishHTML — metrics_report.html not found."
                }
            }
            cleanWs()
        }
    }
}
