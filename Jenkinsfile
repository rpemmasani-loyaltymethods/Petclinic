pipeline {
    agent any

    environment {
        MAVEN_HOME = tool name: 'maven3'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/rpemmasani-loyaltymethods/Petclinic.git'
            }
        }

        stage('Build and Test') {
            steps {
                sh 'mvn clean verify'
            }
        }

        stage('Publish JaCoCo Report') {
            steps {
                publishHTML([
                    reportDir: 'target/site/jacoco',
                    reportFiles: 'index.html',
                    reportName: 'JaCoCo Report',
                    keepAll: true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: true
                ])
            }
        }

        stage('Dummy Coverage Summary') {
            steps {
                script {
                    // Fake values for demo
                    def lineCoverage = 83.5
                    def branchCoverage = 77.2
                    def color = lineCoverage >= 80 ? 'GREEN' : lineCoverage >= 50 ? 'YELLOW' : 'RED'

                    // Use badges plugin to show it in build summary area
                    addBadge(icon: "graph.png", text: "Line: ${lineCoverage}%", color: color)
                    addBadge(icon: "graph.png", text: "Branch: ${branchCoverage}%", color: color)
                }
            }
        }
    }

    post {
        always {
            recordCoverage tools: [[parser: 'JACOCO', pattern: 'target/site/jacoco/jacoco.xml']]
        }
    }
}