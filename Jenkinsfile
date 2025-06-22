pipeline {
    agent any

    parameters {
        string(name: 'SONAR_PROJECT_KEY', defaultValue: 'Petclinic', description: 'SonarQube Project Key')
        string(name: 'SONAR_PROJECT_NAME', defaultValue: 'Petclinic', description: 'SonarQube Project Name')
        choice(name: 'QUALITY_GATE', choices: ['Sonar way', 'Default-Quality-Gate', 'Main-Quality-Gate', 'Feature-Quality-Gate'], description: 'Quality gate to apply')
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

        stage('Test & Coverage') {
            steps {
                sh 'mvn clean verify'
            }
        }

        stage('Fetch SonarQube Metrics') {
            steps {
                script {
                    def metricsURL = "${env.SONARQUBE_URL}/api/measures/component?component=${params.SONAR_PROJECT_KEY}&metricKeys=line_coverage,branch_coverage,lines_to_cover,uncovered_lines,coverage"

                    withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                        sh """
                            mkdir -p archive
                            curl -s -H "Authorization: Basic \$(echo -n ${SONARQUBE_TOKEN}: | base64)" "${metricsURL}" > archive/sonar_metrics.json
                        """
                    }
                }
            }
        }

        stage('Generate Dummy Coverage Summary Visual') {
            steps {
                script {
                    def htmlContent = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Coverage Summary</title>
</head>
<body>
    <h3 style="margin-bottom:8px;">Code Coverage – 83.5% (200/240 lines)</h3>

    <b>Conditionals (Branches)</b><br/>
    <div style="width:300px;height:24px;background:#eee;display:flex;font-weight:bold;font-size:13px;">
      <div style="width:75%;background:limegreen;color:#222;text-align:right;padding-right:4px;">
        75.0%
      </div>
      <div style="width:25%;background:#c00;"></div>
    </div><br/>

    <b>Statements (Lines)</b><br/>
    <div style="width:300px;height:24px;background:#eee;display:flex;font-weight:bold;font-size:13px;">
      <div style="width:83.5%;background:limegreen;color:#222;text-align:right;padding-right:4px;">
        83.5%
      </div>
      <div style="width:16.5%;background:#c00;"></div>
    </div>
</body>
</html>
"""
                    writeFile file: 'archive/coverage-summary.html', text: htmlContent
                }
            }
        }

        stage('Publish Coverage Summary Tab') {
            steps {
                publishHTML([
                    reportDir: 'archive',
                    reportFiles: 'coverage-summary.html',
                    reportName: 'Coverage Summary',
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true
                ])
            }
        }
    }
}
