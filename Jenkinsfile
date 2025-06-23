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
        JOB_ARCHIVE = "archive"
    }

    stages {
        stage('Git Checkout') {
            steps {
                git branch: "${env.BRANCH_NAME}", changelog: false, poll: false, url: 'https://github.com/rpemmasani-loyaltymethods/Petclinic.git'
                echo "The branch name is: ${env.BRANCH_NAME}"
            }
        }

        stage('Build') {
            steps {
                script {
                    sh "${MAVEN_HOME}/bin/mvn clean install -X"
                }
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
                            curl --header 'Authorization: Basic ${SonarToken}' \
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
                    def sonarUrl = "${SONARQUBE_URL}api/qualitygates/project_status?projectKey=${SONAR_PROJECT_KEY}"

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

        stage('Fetch SonarQube Metrics & Issues') {
            steps {
                script {
                    def qualityGateURL = "${env.SONARQUBE_URL}/api/qualitygates/project_status?projectKey=${params.SONAR_PROJECT_KEY}"
                    def metricsURL = "${env.SONARQUBE_URL}/api/measures/component?component=${params.SONAR_PROJECT_KEY}&metricKeys=ncloc,complexity,violations,coverage,code_smells,line_coverage,branch_coverage,uncovered_lines,lines_to_cover"
                    def issuesURL = "${env.SONARQUBE_URL}/api/issues/search?componentKeys=${params.SONAR_PROJECT_KEY}&ps=500"

                    withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                        sh """
                            mkdir -p ${JOB_ARCHIVE}
                            curl -s -H "Authorization: Basic \$(echo -n ${SONARQUBE_TOKEN}: | base64)" "${qualityGateURL}" > ${JOB_ARCHIVE}/sonar_quality.json
                            curl -s -H "Authorization: Basic \$(echo -n ${SONARQUBE_TOKEN}: | base64)" "${metricsURL}" > ${JOB_ARCHIVE}/sonar_metrics.json
                            curl -s -H "Authorization: Basic \$(echo -n ${SONARQUBE_TOKEN}: | base64)" "${issuesURL}" > ${JOB_ARCHIVE}/sonar_issues.json
                        """
                    }

                    echo "🐍 Running generate_report.py"
                    sh "python3 generate_report.py || echo '[WARN] Report generation failed, continuing build...'"
                }
            }
        }

        stage('Update Build Badge Summary') {
            steps {
                script {
                    def metricsFile = "${env.JOB_ARCHIVE}/sonar_metrics.json"
                    def summary = "🚫 No metrics found"

                    if (fileExists(metricsFile)) {
                        def content = readFile(metricsFile)
                        if (content?.trim()) {
                            def json = readJSON text: content
                            def measures = json.component.measures.collectEntries {
                                [(it.metric): it.value?.replace('%', '')?.toFloat() ?: 0.0]
                            }

                            def coverage       = measures.get("coverage", 0.0)
                            def lineCoverage   = measures.get("line_coverage", 0.0)
                            def branchCoverage = measures.get("branch_coverage", 0.0)
                            def uncovered      = measures.get("uncovered_lines", 0.0)
                            def totalLines     = measures.get("lines_to_cover", 0.0)

                            def coverageIcon = coverage >= 80 ? "✅" : (coverage >= 50 ? "⚠️" : "🔴")
                            def lineIcon     = lineCoverage >= 80 ? "✅" : (lineCoverage >= 50 ? "⚠️" : "🔴")
                            def branchIcon   = branchCoverage >= 80 ? "✅" : (branchCoverage >= 50 ? "⚠️" : "🔴")

                            summary = """
    ${coverageIcon} <b>Total Coverage</b>: ${String.format("%.1f", coverage)}%<br/>
    ${lineIcon} <b>Line Coverage</b>: ${String.format("%.1f", lineCoverage)}%<br/>
    ${branchIcon} <b>Branch Coverage</b>: ${String.format("%.1f", branchCoverage)}%<br/>
    📉 <b>Uncovered Lines</b>: ${uncovered.toInteger()} / ${totalLines.toInteger()}
    """
                        } else {
                            echo "[WARN] sonar_metrics.json is empty."
                        }
                    } else {
                        echo "[WARN] sonar_metrics.json not found."
                    }

                    currentBuild.description = summary
                }
            }
        }

        stage('Publish JaCoCo HTML Report') {
            steps {
                publishHTML([
                    reportDir: 'target/site/jacoco',
                    reportFiles: 'index.html',
                    reportName: 'JaCoCo Coverage Report',
                    keepAll: true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: true
                ])
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
            script {
                echo "Publishing Metrics Report..."
                def htmlPath = "${env.JOB_ARCHIVE}/metrics_report.html"
                if (fileExists(htmlPath)) {
                    publishHTML([
                        reportName: "SonarQube #${env.BUILD_NUMBER}",
                        reportDir: "${env.JOB_ARCHIVE}",
                        reportFiles: 'metrics_report.html',
                        keepAll: true,
                        allowMissing: false,
                        alwaysLinkToLastBuild: true
                    ])
                } else {
                    echo "[WARN] metrics_report.html not found, skipping publishHTML"
                }
            }
        }
    }
}
