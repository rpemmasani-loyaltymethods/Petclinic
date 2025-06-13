pipeline {
    agent any

    parameters {
        string(name: 'SONAR_PROJECT_KEY', description: 'Unique identifier')
        string(name: 'SONAR_PROJECT_NAME', description: 'Name of the project')
        choice(name: 'QUALITY_GATE', choices: ['Sonar way', 'Default-Quality-Gate', 'Main-Quality-Gate', 'Feature-Quality-Gate'], description: 'Which quality gate you want to apply.')
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
                echo "The branch name is: ${env.BRANCH_NAME}"
            }
        }

        stage('Build & Test') {
            steps {
                script {
                    sh "${MAVEN_HOME}/bin/mvn clean install -X"
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def branchName = "main"
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
                        curl --header 'Authorization: Basic ${SonarToken}'  \
                        --location '${SONARQUBE_URL}api/qualitygates/select?projectKey=${SONAR_PROJECT_KEY}' \
                        --data-urlencode 'gateName=${qualityGate}'
                        """
                    }

                    echo 'Sleeping for 2 minutes after SonarQube analysis...'
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
                        def sonarStatus = sonarData?.projectStatus?.status ?: 'Unknown'
                        def conditions = sonarData?.projectStatus?.conditions ?: []

                        echo "SonarQube Quality Gate Status: ${sonarStatus}"

                        def testCases = ""
                        testCases += "<testcase classname='SonarQube' name='QualityGateStatus'>"
                        if (sonarStatus != 'OK') {
                            testCases += "<failure message='Quality Gate Failed'>Status: ${sonarStatus}</failure>"
                        }
                        testCases += "</testcase>"

                        conditions.each { cond ->
                            def failed = cond.status != 'OK'
                            testCases += "<testcase classname='SonarQube' name='${cond.metricKey}'>"
                            if (failed) {
                                testCases += "<failure message='Metric failed'>Metric: ${cond.metricKey}, Value: ${cond.actualValue}, Threshold: ${cond.errorThreshold}</failure>"
                            }
                            testCases += "</testcase>"
                        }

                        def junitXml = """<?xml version='1.0' encoding='UTF-8'?>
<testsuite name='SonarQubeQualityGate' tests='${conditions.size() + 1}' failures='${conditions.count { it.status != 'OK' } + (sonarStatus != 'OK' ? 1 : 0)}' errors='0' skipped='0'>
${testCases}
</testsuite>
"""
                        sh 'mkdir -p target/surefire-reports'
                        writeFile file: 'target/surefire-reports/sonartest.xml', text: junitXml

                        def htmlContent = """<!DOCTYPE html><html><head><title>SonarQube Quality Gate Report</title>
<style>body{font-family:Arial;}table{width:100%;border-collapse:collapse;}th,td{padding:8px;border:1px solid #ccc;text-align:left;}th{background:#f4f4f4;}</style>
</head><body><h1>SonarQube Quality Gate Report</h1><p><strong>Status:</strong> ${sonarStatus}</p><table><tr><th>Metric</th><th>Status</th><th>Actual</th><th>Threshold</th><th>Comparator</th></tr>
"""
                        conditions.each { cond ->
                            def rowColor = cond.status == 'OK' ? '#dfd' : '#fdd'
                            htmlContent += "<tr style='background:${rowColor}'><td>${cond.metricKey}</td><td>${cond.status}</td><td>${cond.actualValue}</td><td>${cond.errorThreshold}</td><td>${cond.comparator}</td></tr>"
                        }
                        htmlContent += "</table></body></html>"

                        sh 'mkdir -p archive'
                        writeFile file: 'archive/sonar_quality_gate_report.html', text: htmlContent

                        if (sonarStatus != 'OK') {
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
            script {
                echo "Publishing Metrics Report..."
                publishHTML([
                    reportName: "SonarQube Metrics Report ${env.BUILD_NUMBER}",
                    reportDir: 'archive',
                    reportFiles: 'sonar_quality_gate_report.html',
                    keepAll: true,
                    allowMissing: false,
                    alwaysLinkToLastBuild: true
                ])
            }
        }
    }
}
