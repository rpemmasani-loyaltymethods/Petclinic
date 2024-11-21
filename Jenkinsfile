pipeline {
    agent any
    environment {
        SONARQUBE_SERVER = 'Sonarqube-8.9.2'
        SONAR_PROJECT_KEY = 'Petclinic'
        SONAR_PROJECT_NAME = 'Petclinic'
        MAVEN_HOME = tool name: 'maven3'
        SONARQUBE_URL = "https://sonarqube.devops.lmvi.net/"

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
                    withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                        sh """
                        ${MAVEN_HOME}/bin/mvn sonar:sonar \
                        -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                        -Dsonar.projectName=${SONAR_PROJECT_NAME} \
                        -Dsonar.host.url=${SONARQUBE_URL} \
                        -Dsonar.login=${SONARQUBE_TOKEN} \
                        -Dsonar.ws.timeout=600 \
                        """
                    }
                }
            }
        }
		stage ("Quality Gate") {
		   steps {
			  withSonarQubeEnv('SonarQube') {
				 sh "../../../sonar-scanner-6.2.0.4584/bin/sonar-scanner"   
			  }

			  def qualitygate = waitForQualityGate()
			  if (qualitygate.status != "OK") {
				 error "Pipeline aborted due to quality gate coverage failure: ${qualitygate.status}"
			  }
		   }
		}
        stage('Post-build Actions') {
            steps {
                echo 'Post-build actions can be added here.'
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

