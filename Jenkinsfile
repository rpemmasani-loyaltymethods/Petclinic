pipeline {
    agent any

    parameters {
        string(name: 'SONAR_PROJECT_KEY', description: 'Unique identifier')
        string(name: 'SONAR_PROJECT_NAME', description: 'Name of the project')
        choice(name: 'QUALITY_GATE', choices: ['Sonar way', 'Default-Quality-Gate', 'Main-Quality-Gate', 'Feature-Quality-Gate'], description: 'Quality gate to apply')
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
                echo "Branch: ${env.BRANCH_NAME}"
            }
        }

        stage('Build & Test') {
            steps {
                sh "${MAVEN_HOME}/bin/mvn clean install"
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def qualityGate = "${params.QUALITY_GATE}"

                    withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                        sh """
                            ${MAVEN_HOME}/bin/mvn sonar:sonar \
                            -Dsonar.projectKey=${params.SONAR_PROJECT_KEY} \
                            -Dsonar.projectName=${params.SONAR_PROJECT_NAME} \
                            -Dsonar.host.url=${SONARQUBE_URL} \
                            -Dsonar.login=${SONARQUBE_TOKEN} \
                            -Dsonar.ws.timeout=600
                        """
                    }

                    withCredentials([string(credentialsId: 'SonarToken', variable: 'SonarToken')]) {
                        sh """
                            curl -s --header 'Authorization: Basic ${SonarToken}' \
                            --location '${SONARQUBE_URL}api/qualitygates/select?projectKey=${params.SONAR_PROJECT_KEY}' \
                            --data-urlencode 'gateName=${qualityGate}'
                        """
                    }

                    echo 'Sleeping 2 minutes to wait for SonarQube Quality Gate result...'
                    sleep(time: 2, unit: 'MINUTES')
                }
            }
        }

        stage('Check Quality Gate') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    script {
                        def sonarUrl = "${SONARQUBE_URL}api/qualitygates/project_status?projectKey=${params.SONAR_PROJECT_KEY}"
                        withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                            sh "curl -s -u ${SONARQUBE_TOKEN}: ${sonarUrl} > sonar_status.json"
                        }
                        def sonarStatusJson = readFile('sonar_status.json')
                        def sonarData = new groovy.json.JsonSlurper().parseText(sonarStatusJson)
                        def status = sonarData?.projectStatus?.status ?: 'Unknown'
                        echo "SonarQube Quality Gate Status: ${status}"

                        if (status != 'OK') {
                            error "Quality Gate Failed! Status: ${status}"
                        }
                    }
                }
            }
        }

        stage('Publish Test Results') {
            steps {
                sh 'mkdir -p target/surefire-reports' // Ensure dir exists
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

        stage('Debug Workspace') {
            steps {
                sh 'pwd && ls -lR'
            }
        }

        stage('Fetch and Convert Metrics') {
            steps {
                script {
                    def metricsUrl = "${SONARQUBE_URL}api/measures/component?component=${params.SONAR_PROJECT_KEY}&metricKeys=ncloc,complexity,violations,coverage,code_smells,security_hotspots,bugs,vulnerabilities,tests,duplicated_lines,alert_status"
                    withCredentials([string(credentialsId: 'SonarToken', variable: 'SonarToken')]) {
                        sh """
                            curl -s --location '${metricsUrl}' \
                            --header 'Authorization: Basic ${SonarToken}' > metrics.json
                        """
                    }

                    def metricsJson = readFile('metrics.json')
                    def parsed = new groovy.json.JsonSlurper().parseText(metricsJson)
                    def tableRows = parsed.component.measures.collect {
                        "<tr><td>${it.metric}</td><td>${it.value}</td></tr>"
                    }.join("\n")

                    def htmlContent = """
<!DOCTYPE html>
<html>
<head>
    <title>SonarQube Metrics Report</title>
    <style>
        body { font-family: Arial; margin: 20px; color: #333; }
        h1 { color: #2C3E50; }
        table { border-collapse: collapse; width: 100%; font-size: 14px; }
        th, td { border: 1px solid #ddd; padding: 8px; }
        th { background: #f2f2f2; }
        tr:nth-child(even) { background: #f9f9f9; }
    </style>
</head>
<body>
    <h1>SonarQube Metrics Report</h1>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        ${tableRows}
    </table>
</body>
</html>
"""
                    writeFile file: 'metrics_report.html', text: htmlContent
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed.'
        }
        always {
            cleanWs()
            publishHTML([
                reportName: "SonarQube Metrics Report",
                reportDir: '.', // current workspace
                reportFiles: 'metrics_report.html',
                keepAll: true,
                allowMissing: false,
                alwaysLinkToLastBuild: true
            ])
        }
    }
}
