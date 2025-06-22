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
                echo "Branch: ${env.BRANCH_NAME}"
            }
        }

        stage('Build & Test') {
            steps {
                sh 'mvn clean verify'
            }
        }

        stage('Fetch Sonar Metrics') {
            steps {
                script {
                    def metricsURL = "${SONARQUBE_URL}/api/measures/component?component=${params.SONAR_PROJECT_KEY}&metricKeys=coverage,line_coverage,branch_coverage,uncovered_lines,lines_to_cover"
                    withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                        sh """
                            mkdir -p archive
                            curl -s -H "Authorization: Basic \$(echo -n ${SONARQUBE_TOKEN}: | base64)" "${metricsURL}" > archive/sonar_metrics.json
                            sleep 10
                        """
                    }
                }
            }
        }

        stage('Update Build Badge Summary') {
            steps {
                script {
                    def coverage = 0.0
                    def branchCoverage = 0.0
                    def lineCoverage = 0.0
                    def uncovered = 0
                    def totalLines = 0
                    def summary = "🚫 No metrics found"

                    if (fileExists('archive/sonar_metrics.json')) {
                        def json = readJSON file: 'archive/sonar_metrics.json'
                        def measures = json.component.measures.collectEntries {
                            [(it.metric): it.value?.replace('%', '')?.toFloat() ?: 0.0]
                        }

                        coverage       = measures.get("coverage", 0.0)
                        lineCoverage   = measures.get("line_coverage", 0.0)
                        branchCoverage = measures.get("branch_coverage", 0.0)
                        uncovered      = measures.get("uncovered_lines", 0.0)
                        totalLines     = measures.get("lines_to_cover", 0.0)

                        // Set emoji color based on thresholds
                        def coverageIcon = coverage >= 80 ? "✅" : (coverage >= 50 ? "⚠️" : "🔴")
                        def lineIcon     = lineCoverage >= 80 ? "✅" : (lineCoverage >= 50 ? "⚠️" : "🔴")
                        def branchIcon   = branchCoverage >= 80 ? "✅" : (branchCoverage >= 50 ? "⚠️" : "🔴")

                        summary = """
${coverageIcon} <b>Total Coverage</b>: ${String.format("%.1f", coverage)}%<br/>
${lineIcon} <b>Line Coverage</b>: ${String.format("%.1f", lineCoverage)}%<br/>
${branchIcon} <b>Branch Coverage</b>: ${String.format("%.1f", branchCoverage)}%<br/>
📉 <b>Uncovered Lines</b>: ${uncovered.toInteger()} / ${totalLines.toInteger()}
"""
                    }

                    // Show in build description
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
}
