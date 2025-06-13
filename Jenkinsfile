pipeline {
    agent any

    environment {
        SonarToken = credentials('SonarToken') // Jenkins credential ID for SonarQube token
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build and Test') {
            steps {
                sh './mvnw clean verify'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh './mvnw sonar:sonar'
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 2, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Fetch Sonar Metrics & Generate Report') {
            steps {
                withCredentials([string(credentialsId: 'SonarToken', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        curl --silent --location \
                        "https://sonarqube.devops.lmvi.net/api/measures/component?component=Petclinic&metricKeys=coverage,methods,conditionals,statements" \
                        --header "Authorization: Basic $SONAR_TOKEN" \
                        -o metrics.json
                    '''

                    writeFile file: 'generate_html_report.py', text: '''
import json, os

with open("metrics.json") as f:
    data = json.load(f)

metrics = {m["metric"]: float(m["value"]) for m in data["component"]["measures"]}

def render_bar(label, value):
    green = value
    red = 100 - value
    return f"""
    <div style='margin-bottom: 10px;'>
        <strong>{label} - {value:.1f}%</strong>
        <div style='background:#ddd; border-radius:4px; overflow:hidden; width:100%; height:20px;'>
            <div style='width:{green}%; background:limegreen; height:100%; display:inline-block;'></div>
            <div style='width:{red}%; background:red; height:100%; display:inline-block;'></div>
        </div>
    </div>
    """

html = "<html><body><h2>Code Coverage</h2>"
for key, label in [("coverage", "Total Coverage"), ("methods", "Methods"), ("conditionals", "Conditionals"), ("statements", "Statements")]:
    if key in metrics:
        html += render_bar(label, metrics[key])
html += "</body></html>"

os.makedirs("archive", exist_ok=True)
with open("archive/coverage_report.html", "w") as f:
    f.write(html)
                    '''

                    sh 'python3 generate_html_report.py'
                }
            }
        }

        stage('Publish HTML Report') {
            steps {
                publishHTML(target: [
                    reportName: 'Sonar Coverage Report',
                    reportDir: 'archive',
                    reportFiles: 'coverage_report.html',
                    keepAll: true,
                    alwaysLinkToLastBuild: true
                ])
            }
        }

        stage('JUnit Report') {
            steps {
                junit '**/target/surefire-reports/*.xml'
            }
        }

        stage('Checkstyle Report') {
            steps {
                recordIssues tools: [checkStyle(pattern: '**/target/checkstyle-result.xml')]
            }
        }

        stage('JaCoCo Report') {
            steps {
                jacoco(
                    execPattern: 'target/jacoco.exec',
                    classPattern: 'target/classes',
                    sourcePattern: 'src/main/java',
                    inclusionPattern: '**/*.class',
                    exclusionPattern: ''
                )
            }
        }
    }

    post {
        always {
            echo 'Pipeline completed.'
        }

        failure {
            echo 'Pipeline failed.'
        }
    }
}
