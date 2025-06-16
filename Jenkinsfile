pipeline {
    agent any

    parameters {
        string(name: 'SONAR_PROJECT_KEY', defaultValue: 'Petclinic', description: 'SonarQube Project Key')
    }

    environment {
        SONARQUBE_URL = 'https://sonarqube.devops.lmvi.net/'
    }

    stages {
        stage('Checkout Code') {
            steps {
                git url: 'https://github.com/spring-projects/spring-petclinic.git', branch: 'main'
            }
        }

        stage('Fetch SonarQube Quality Gate Status') {
            steps {
                script {
                    def statusUrl = "${SONARQUBE_URL}api/qualitygates/project_status?projectKey=${params.SONAR_PROJECT_KEY}"

                    withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                        sh """
                            echo "Fetching SonarQube Quality Gate status..."
                            curl -s -u ${SONARQUBE_TOKEN}: "${statusUrl}" > quality_gate.json || echo '{}' > quality_gate.json
                        """
                    }
                }
            }
        }

        stage('Generate SonarQube Report') {
            steps {
                script {
                    sh '''
                        mkdir -p archive
                        python3 generate_report.py
                    '''
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
                    echo '⚠️ Report not found. Skipping publishHTML.'
                }
            }
            cleanWs()
        }
    }
}
