pipeline {
    agent any

    parameters {
        string(name: 'SONAR_PROJECT_KEY', defaultValue: 'Petclinic', description: 'SonarQube Project Key')
        string(name: 'SONAR_PROJECT_NAME', defaultValue: 'Petclinic', description: 'SonarQube Project Name')
        choice(name: 'QUALITY_GATE', choices: ['Sonar way', 'Default-Quality-Gate', 'Main-Quality-Gate', 'Feature-Quality-Gate'], description: 'Which quality gate you want to apply.')
    }

    environment {
        SONARQUBE_SERVER = 'Sonarqube-8.9.2'
        MAVEN_HOME = tool name: 'maven3'
        SONARQUBE_URL = "https://sonarqube.devops.lmvi.net"
        SONARQUBE_TOKEN = credentials('SONARQUBE_TOKEN')
    }

    stages {
        stage('Git Checkout') {
            steps {
                git branch: "${env.BRANCH_NAME}", changelog: false, poll: false, url: 'https://github.com/rpemmasani-loyaltymethods/Petclinic.git'
                echo "The branch name is: ${env.BRANCH_NAME}"
            }
        }

        stage('Fetch SonarQube Quality Gate and Metrics') {
            steps {
                script {
                    def qualityGateURL = "${env.SONARQUBE_URL}/api/qualitygates/project_status?projectKey=${params.SONAR_PROJECT_KEY}"
                    def metricsURL = "${env.SONARQUBE_URL}/api/measures/component?component=${params.SONAR_PROJECT_KEY}&metricKeys=ncloc,complexity,violations,coverage,code_smells"
                    def issuesURL = "${env.SONARQUBE_URL}/api/issues/search?componentKeys=${params.SONAR_PROJECT_KEY}&ps=500"

                    withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                        sh """
                            mkdir -p archive
                            curl -s -H "Authorization: Basic \$(echo -n ${SONARQUBE_TOKEN}: | base64)" "${qualityGateURL}" > archive/sonar_quality.json 
                            curl -s -H "Authorization: Basic \$(echo -n ${SONARQUBE_TOKEN}: | base64)" "${metricsURL}" > archive/sonar_metrics.json
                            curl -s -H "Authorization: Basic \$(echo -n ${SONARQUBE_TOKEN}: | base64)" "${issuesURL}" > archive/sonar_issues.json
                        """
                    }

                    echo "🐍 Running generate_report.py"
                    sh 'python3 generate_report.py || echo "[WARN] Report generation failed, continuing build..."'
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
                jacoco execPattern: 'target/jacoco.exec', classPattern: 'target/classes', sourcePattern: 'src/main/java'
            }
        }

        stage('Convert SonarQube Issues to Checkstyle') {
            steps {
                script {
                    echo ${WORKSPACE}/archive
                    sh 'python3 sonar_to_checkstyle.py'
                    recordIssues tools: [checkStyle(pattern: 'archive/sonar_checkstyle.xml')]
                    echo "Checkstyle issues recorded."
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
                            reportName: 'SonarQube Metrics Report ${env.BUILD_NUMBER}',
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
            echo "Cleaning up workspace..."
        }
    }
}