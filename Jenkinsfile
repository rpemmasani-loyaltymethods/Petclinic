pipeline {
    agent any
    environment {
        SONARQUBE_SERVER = 'Sonarqube-8.9.2'
        SONAR_PROJECT_KEY = 'Petclinic'
        SONAR_PROJECT_NAME = 'Petclinic'
        MAVEN_HOME = tool name: 'maven3'
        SONARQUBE_URL = "https://sonarqube.devops.lmvi.net/"
        SONARQUBE_TOKEN = credentials('SONARQUBE_TOKEN')
    }

    stages {
        stage('Git Checkout') {
            steps {
                git branch: 'main', changelog: false, poll: false, url: 'https://github.com/rpemmasani-loyaltymethods/Petclinic.git'
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
                    def branchName = env.BRANCH_NAME
                    def qualityGate

                    // Define quality gate based on the branch
                    if (branchName == 'main') {
                        qualityGate = 'Main-Quality-Gate'  // Quality gate for main branch
                    } else if (branchName.startsWith('feature/')) {
                        qualityGate = 'Feature-Quality-Gate' // Quality gate for feature branches
                    } else {
                        qualityGate = 'Default-Quality-Gate' // Quality gate for other branches
                    }

                    withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                        sh """
                        ${MAVEN_HOME}/bin/mvn sonar:sonar \
                        -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                        -Dsonar.projectName=${SONAR_PROJECT_NAME} \
                        -Dsonar.branch.name=${branchName} \
                        -Dsonar.host.url=${SONARQUBE_URL} \
                        -Dsonar.login=${SONARQUBE_TOKEN} \
                        -Dsonar.qualitygate=${qualityGate} \
                        -Dsonar.ws.timeout=600
                        """
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                script {
                    // Define SonarQube project status API URL
                    def sonarUrl = "${SONARQUBE_URL}api/qualitygates/project_status?projectKey=${SONAR_PROJECT_KEY}"

                    withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                        // Fetch the quality gate status and write it to a file
                        sh """
                            curl -s -u ${SONARQUBE_TOKEN}: ${sonarUrl} > sonar_status.json
                        """

                        // Use Python to process the JSON file and check the quality gate status
                        sh """
                            python3 -c '
import json
import sys
# Read the JSON file
with open("sonar_status.json", "r") as f:
    data = json.load(f)
# Extract relevant information from the JSON
sonarStatus = data.get("projectStatus", {}).get("status", "Unknown")
print(sonarStatus)
if sonarStatus != "OK":
    print("Quality Gate failed! SonarQube status: {}".format(sonarStatus))
    sys.exit(1)  # Exit with status code 1 to fail the pipeline
                            '
                        """
                    }
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
        }
    }
}

