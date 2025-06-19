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
                    def metricsURL = "${env.SONARQUBE_URL}/api/measures/component?component=${params.SONAR_PROJECT_KEY}&metricKeys=statements,uncovered_lines,functions,conditions_to_cover,lines_to_cover,branch_coverage,line_coverage,bugs,ncloc,complexity,violations,coverage,code_smells,security_hotspots,bugs,vulnerabilities,tests,duplicated_lines,alert_status"
                    def issuesURL = "${env.SONARQUBE_URL}/api/issues/search?componentKeys=${params.SONAR_PROJECT_KEY}&ps=500"

                    withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                        sh """
                            mkdir -p archive
                            curl -s -H "Authorization: Basic \$(echo -n ${SONARQUBE_TOKEN}: | base64)" "${qualityGateURL}" > archive/sonar_quality.json 
                            curl -s -H "Authorization: Basic \$(echo -n ${SONARQUBE_TOKEN}: | base64)" "${metricsURL}" > archive/sonar_metrics.json
                            sleep 30
                        """
                    }

                    echo "🐍 Running generate_report.py (combined HTML)"
                    sh 'python3 generate_report.py || echo "[WARN] Report generation failed, continuing build..."'
                    sh 'python3 generate_cobertura_xml.py || echo "[WARN] Report generate_cobertura_xml failed, continuing build..."'
                }
            }
        }

        stage('Build & Test') {
            steps {
                withMaven(maven: 'maven3') {
                    sh 'mvn clean verify'
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
        stage('Publish Coverage Report') {
            steps {
                cobertura coberturaReportFile: 'archive/sonar_cobertura.xml'
            }
        }

    }
    post {
        always {
            script {
                // ✅ Native right-side bar
                // recordCoverage tools: [jacoco()]

                // ✅ Combined SonarQube report with bars + metrics
                if (fileExists('archive/combined_metrics_report.html')) {
                    publishHTML(target: [
                        reportDir: 'archive',
                        reportFiles: 'combined_metrics_report.html',
                        reportName: 'SonarQube Combined Report',
                        keepAll: true,
                        alwaysLinkToLastBuild: true,
                        allowMissing: false
                    ])
                } else {
                    echo "⚠️ Skipping publishHTML — combined_metrics_report.html not found."
                }
            }
        }
    }
}
