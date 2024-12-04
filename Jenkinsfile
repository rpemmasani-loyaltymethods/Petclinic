pipeline {
    agent any
    
    parameters {
        // Parameter to specify the branch name, default is 'main'
        string(name: 'BRANCH_NAME', defaultValue: 'main', description: 'Branch to build')
		string(name: 'SONAR_PROJECT_KEY', description: 'unique identifier')
		string(name: 'SONAR_PROJECT_NAME', description: 'name of the project')
    }

    environment {
        SONARQUBE_SERVER = 'Sonarqube-8.9.2'
        MAVEN_HOME = tool name: 'maven3'
        SONARQUBE_URL = "https://sonarqube.devops.lmvi.net/"
        SonarToken = credentials('SonarToken')
    }

    stages {
        stage('Git Checkout') {
            steps {
                // Dynamically use the branch name from the parameter
                git branch: "${params.BRANCH_NAME}", changelog: false, poll: false, url: 'https://github.com/rpemmasani-loyaltymethods/Petclinic.git'
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
                    // def branchName = sh(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim()
                    // echo "SonarQube Quality env.BRANCH_NAME: ${branchName}"
                    def branchName = "${params.BRANCH_NAME}"

                    // Define quality gate based on the branch
                    if (branchName == 'main') {
                        qualityGate = 'Main-Quality-Gate'  // Quality gate for main branch
                        echo "Applying : ${qualityGate} in SonarQube"
                    } else if (branchName.startsWith('feature')) {
                        qualityGate = 'Feature-Quality-Gate' // Quality gate for feature branches
                        echo "Applying : ${qualityGate} in SonarQube"
                    } else {
                        qualityGate = 'Default-Quality-Gate' // Quality gate for other branches
                        echo "Applying : ${qualityGate} in SonarQube"
                    }

                    withCredentials([string(credentialsId: 'SonarToken', variable: 'SonarToken')]) {
                        // SonarQube Analysis
                        sh """
                        ${MAVEN_HOME}/bin/mvn sonar:sonar \
                        -Dsonar.projectKey=${params.SONAR_PROJECT_KEY} \
                        -Dsonar.projectName=${params.SONAR_PROJECT_NAME} \
                        -Dsonar.host.url=${SONARQUBE_URL} \
                        -Dsonar.login=${SonarToken} \
                        -Dsonar.ws.timeout=600
                        """
                    }

                    withCredentials([string(credentialsId: 'SonarToken', variable: 'SonarToken')]) {
                        // Set quality gate via SonarQube API (with proper credentials and URL)
                        sh """
                        curl --header 'Authorization: Basic ${SonarToken}' \
                        --location '${SONARQUBE_URL}api/qualitygates/set_as_default' \
                        --data-urlencode "name=${qualityGate}"
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

                    withCredentials([string(credentialsId: 'SonarToken', variable: 'SonarToken')]) {
                        // Fetch the quality gate status and write it to a file
                        sh """
                            curl -s -u ${SonarToken}: ${sonarUrl} > sonar_status.json
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
