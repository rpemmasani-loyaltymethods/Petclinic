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

        stage('Test & Coverage') {
            steps {
                sh 'mvn clean verify'
            }
        }

        stage('Fetch SonarQube Quality Gate and Metrics') {
            steps {
                script {
                    def qualityGateURL = "${env.SONARQUBE_URL}/api/qualitygates/project_status?projectKey=${params.SONAR_PROJECT_KEY}"
                    def metricsURL = "${env.SONARQUBE_URL}/api/measures/component?component=${params.SONAR_PROJECT_KEY}&metricKeys=statements,uncovered_lines,functions,conditions_to_cover,lines_to_cover,branch_coverage,line_coverage,bugs,ncloc,complexity,violations,coverage,code_smells,security_hotspots,bugs,vulnerabilities,tests,duplicated_lines,alert_status"

                    withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                        sh """
                            mkdir -p archive
                            curl -s -H "Authorization: Basic \$(echo -n ${SONARQUBE_TOKEN}: | base64)" "${qualityGateURL}" > archive/sonar_quality.json 
                            curl -s -H "Authorization: Basic \$(echo -n ${SONARQUBE_TOKEN}: | base64)" "${metricsURL}" > archive/sonar_metrics.json
                            sleep 30
                        """
                    }

                    echo "✅ Sonar metrics downloaded. Skipping generate_cobertura_xml.py as per new requirement."
                }
            }
        }

        stage('Publish JaCoCo Report') {
            steps {
                publishHTML([
                    reportDir: 'target/site/jacoco',
                    reportFiles: 'index.html',
                    reportName: 'JaCoCo Coverage Report',
                    keepAll: true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: false
                ])
            }
        }

        stage('Set Build Description with Coverage Summary') {
            steps {
                script {
                    def summary = ""
                    if (fileExists('archive/sonar_metrics.json')) {
                        def json = readJSON file: 'archive/sonar_metrics.json'
                        def measures = json.component.measures.collectEntries {
                            [(it.metric): it.value?.replace('%', '')?.toFloat() ?: 0.0]
                        }

                        def lineCoverage    = measures.get("line_coverage", 0)
                        def branchCoverage  = measures.get("branch_coverage", 0)
                        def methodCoverage  = measures.get("functions", 0)
                        def totalLines      = measures.get("lines_to_cover", 0)
                        def uncoveredLines  = measures.get("uncovered_lines", 0)
                        def coveredLines    = totalLines - uncoveredLines
                        def coveragePercent = measures.get("coverage", 0)

                        summary = """
<h3 style="margin-bottom:8px;">Code Coverage – ${String.format('%.1f', coveragePercent)}% (${coveredLines.toInteger()}/${totalLines.toInteger()} elements)</h3>
<div style="border:1px solid #ccc;padding:8px;width:max-content;">

<b>Methods</b> <span style="float:right;">${String.format('%.0f', methodCoverage)}%</span><br/>
<div style="width:300px;height:18px;background:#eee;">
  <div style="width:${methodCoverage}%;background:limegreen;height:100%;display:inline-block;"></div>
  <div style="width:${100 - methodCoverage}%;background:#c00;height:100%;display:inline-block;"></div>
</div><br/>

<b>Conditionals</b> <span style="float:right;">${String.format('%.0f', branchCoverage)}%</span><br/>
<div style="width:300px;height:18px;background:#eee;">
  <div style="width:${branchCoverage}%;background:limegreen;height:100%;display:inline-block;"></div>
  <div style="width:${100 - branchCoverage}%;background:#c00;height:100%;display:inline-block;"></div>
</div><br/>

<b>Statements</b> <span style="float:right;">${String.format('%.0f', lineCoverage)}%</span><br/>
<div style="width:300px;height:18px;background:#eee;">
  <div style="width:${lineCoverage}%;background:limegreen;height:100%;display:inline-block;"></div>
  <div style="width:${100 - lineCoverage}%;background:#c00;height:100%;display:inline-block;"></div>
</div>

</div>
"""
                    } else {
                        summary = "⚠️ Sonar metrics not found."
                    }

                    currentBuild.description = summary
                }
            }
        }
    }

    post {
        always {
            script {
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
