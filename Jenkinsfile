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
                        --location '${SONARQUBE_URL}api/qualitygates/select?projectKey=${params.SONAR_PROJECT_KEY}' \
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

                        // Generate JUnit XML
                        def writer = new StringWriter()
                        def xml = new groovy.xml.MarkupBuilder(writer)

                        def failedConditions = conditions.findAll { it.status != 'OK' }
                        def totalTests = conditions.size() + 1
                        def failures = (sonarStatus != 'OK' ? 1 : 0) + failedConditions.size()

                        xml.testsuite(name: 'SonarQubeQualityGate', tests: totalTests, failures: failures, errors: 0, skipped: 0) {
                            testcase(classname: 'SonarQube', name: 'QualityGateStatus') {
                                if (sonarStatus != 'OK') {
                                    failure(message: "Quality Gate Failed", "Status: ${sonarStatus}")
                                }
                            }

                            conditions.each { cond ->
                                testcase(classname: 'SonarQube', name: cond.metricKey ?: 'unknown') {
                                    if (cond.status != 'OK') {
                                        failure(message: "Metric failed", "Metric: ${cond.metricKey}, Value: ${cond.actualValue}, Threshold: ${cond.errorThreshold}")
                                    }
                                }
                            }
                        }

                        new File("target/surefire-reports").mkdirs()
                        writeFile file: 'target/surefire-reports/sonartest.xml', text: writer.toString()

                        // Generate HTML report
                        def htmlContent = """\
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>SonarQube Quality Gate Report</title>
<style>
body { font-family: Arial; margin: 20px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px; border: 1px solid #ccc; text-align: left; }
th { background-color: #f4f4f4; }
tr.failed { background-color: #fdd; }
tr.ok { background-color: #dfd; }
</style></head><body>
<h1>SonarQube Quality Gate Report</h1>
<p><strong>Project Key:</strong> ${params.SONAR_PROJECT_KEY}</p>
<p><strong>Status:</strong> <span style="color:${sonarStatus == 'OK' ? 'green' : 'red'}">${sonarStatus}</span></p>
<table><thead><tr><th>Metric</th><th>Status</th><th>Actual</th><th>Threshold</th><th>Comparator</th></tr></thead><tbody>
"""

                        conditions.each { cond ->
                            def rowClass = cond.status == 'OK' ? 'ok' : 'failed'
                            htmlContent += "<tr class='${rowClass}'><td>${cond.metricKey}</td><td>${cond.status}</td><td>${cond.actualValue}</td><td>${cond.errorThreshold}</td><td>${cond.comparator}</td></tr>\n"
                        }

                        htmlContent += "</tbody></table></body></html>"

                        new File('archive').mkdirs()
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
                jacoco execPattern: 'target/jacoco.exec', classPattern: 'target/classes', sourcePattern: 'src/main/java'
            }
        }

        stage('Publish Checkstyle Report') {
            steps {
                recordIssues tools: [checkStyle(pattern: 'target/checkstyle-result.xml')]
            }
        }

        stage('Fetch and Convert Metrics') {
            steps {
                script {
                    def metricsUrl = "${SONARQUBE_URL}api/measures/component?component=${params.SONAR_PROJECT_KEY}&metricKeys=ncloc,complexity,violations,coverage,code_smells,security_hotspots,bugs,vulnerabilities,tests,duplicated_lines,alert_status"
                    withCredentials([string(credentialsId: 'SonarToken', variable: 'SonarToken')]) {
                        sh """
                        curl --location '${metricsUrl}' \
                        --header 'Authorization: Basic ${SonarToken}' > metrics.json
                        """
                    }

                    def metricsJson = readJSON file: 'metrics.json'
                    def htmlContent = """<!DOCTYPE html><html><head><title>SonarQube Metrics Report</title>
<style>body{font-family:Arial;}table{width:100%;border-collapse:collapse;}th,td{padding:8px;border:1px solid #ccc;text-align:left;}th{background:#f4f4f4;}</style>
</head><body><h1>SonarQube Metrics Report</h1><table><tr><th>Metric</th><th>Value</th></tr>
"""
                    metricsJson.component.measures.each {
                        htmlContent += "<tr><td>${it.metric}</td><td>${it.value}</td></tr>\n"
                    }
                    htmlContent += "</table></body></html>"
                    new File("archive").mkdirs()
                    writeFile file: 'archive/metrics_report.html', text: htmlContent
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
            script {
                publishHTML([
                    reportName: "SonarQube Metrics Report ${env.BUILD_NUMBER}",
                    reportDir: 'archive',
                    reportFiles: 'metrics_report.html',
                    keepAll: true,
                    allowMissing: false,
                    alwaysLinkToLastBuild: true
                ])

                publishHTML([
                    reportName: "SonarQube Quality Gate Report",
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
