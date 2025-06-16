pipeline {
    agent any

    parameters {
        string(name: 'SONAR_PROJECT_KEY', defaultValue: 'Petclinic', description: 'SonarQube Project Key')
    }

    environment {
        SONARQUBE_URL = 'https://sonarqube.devops.lmvi.net'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/rpemmasani-loyaltymethods/Petclinic.git'
            }
        }

        stage('Fetch SonarQube Quality Gate and Metrics') {
            steps {
                script {
                    def qualityGateURL = "${env.SONARQUBE_URL}/api/qualitygates/project_status?projectKey=${params.SONAR_PROJECT_KEY}"
                    def metricsURL = "${env.SONARQUBE_URL}/api/measures/component?component=${params.SONAR_PROJECT_KEY}&metricKeys=ncloc,complexity,violations,coverage,code_smells"

                    // Fetch responses and save to files
                    sh """
                        curl -s '${qualityGateURL}' -o sonar_quality.json
                        curl -s '${metricsURL}' -o sonar_metrics.json
                    """

                    // Generate HTML report
                    sh 'python3 generate_report.py'
                }
            }
        }

        stage('Publish HTML Report') {
            steps {
                script {
                    if (fileExists('archive/metrics_report.html')) {
                        publishHTML(target: [
                            reportDir: 'archive',
                            reportFiles: 'metrics_report.html',
                            reportName: 'SonarQube Metrics Report',
                            keepAll: true,
                            alwaysLinkToLastBuild: true,
                            allowMissing: false
                        ])
                    } else {
                        echo "⚠️ Skipping publishHTML — metrics_report.html not found."
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}