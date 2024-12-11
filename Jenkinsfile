pipeline {
    agent any
    
    parameters {
        // Parameter to specify the branch name, default is 'main'
        // string(name: 'BRANCH_NAME', defaultValue: 'main', description: 'Branch to build')
		string(name: 'SONAR_PROJECT_KEY', description: 'Unique identifier')
		string(name: 'SONAR_PROJECT_NAME', description: 'Name of the project')
		choice(name: 'QUALITY_GATE', choices: ['Sonar way', 'Default-Quality-Gate', 'Main-Quality-Gate', 'Feature-Quality-Gate'], description: 'Which qualitygate you wanted apply..')
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
                // Dynamically use the branch name from the parameter
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
                    // echo "SonarQube Quality env.BRANCH_NAME: ${branchName}"
                    def branchName = "${env.BRANCH_NAME}"
					def qualityGate = "${params.QUALITY_GATE}"

                    withCredentials([string(credentialsId: 'SONARQUBE_TOKEN', variable: 'SONARQUBE_TOKEN')]) {
                        // SonarQube Analysis
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
                        // Set quality gate via SonarQube API (with proper credentials and URL)
                        sh """
                        curl --header 'Authorization: Basic ${SonarToken}' \
                        --location '${SONARQUBE_URL}api/qualitygates/select?projectKey=${SONAR_PROJECT_KEY}' \
                        --data-urlencode 'gateName=${qualityGate}'
                        """
                    }


                    // Sleep for 2 minutes after SonarQube analysis
                    echo 'Sleeping for 2 minutes after SonarQube analysis...'
                    sleep(time: 2, unit: 'MINUTES')
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
                        // Groovy script to check the quality gate status from the JSON file
                        def sonarStatusJson = readFile('sonar_status.json')
                        def sonarData = new groovy.json.JsonSlurper().parseText(sonarStatusJson)
                        echo "SonarQube Response Json: ${sonarData}"
                        // Extract relevant information from the JSON
                        def sonarStatus = sonarData?.projectStatus?.status ?: 'Unknown'
                        echo "SonarQube Quality Gate Status: ${sonarStatus}"

                        if (sonarStatus != 'OK') {
                            echo "Quality Gate failed! SonarQube status: ${sonarStatus}"
                            currentBuild.result = 'FAILURE'  // Mark the build as failed
                            error "Quality Gate Failed!"  // Terminate the build with failure
                        }
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
