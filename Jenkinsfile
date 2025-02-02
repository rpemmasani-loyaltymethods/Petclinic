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
                    // echo "SonarQube Quality env.BRANCH_NAME: ${branchName}"
                    def branchName = "main"
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
        stage('Fetch and Convert Metrics') {
            steps {
                script {
                    def metricsUrl = "${SONARQUBE_URL}api/measures/component?component=${params.SONAR_PROJECT_KEY}&metricKeys=ncloc,complexity,violations,coverage,code_smells,security_hotspots,bugs,vulnerabilities,tests,duplicated_lines,alert_status"
                    withCredentials([string(credentialsId: 'SonarToken', variable: 'SonarToken')]) {
                        sh """
                        curl --location '${metricsUrl}' \
                        --header 'Authorization: Basic ${SonarToken}' > metrics.json
                        """
                    }
                    script {
                        // Read the JSON data from metrics.json file
                        def metricsJson = readFile('metrics.json')

                        // Generate Python script dynamically to create the HTML report
                        def pythonScript = """
import json

# Load the JSON data from the metrics.json file
with open('metrics.json', 'r') as f:
    data = json.load(f)

# HTML content for the report
html_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>SonarQube Metrics Report</title>
    <style>
        body {
            font-family: Arial, Helvetica, sans-serif;
            margin: 20px;
            color: #333;
        }
        h1 {
            color: #2C3E50;
            text-align: center;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px auto;
            font-size: 14px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f9f9f9;
            color: #333;
            font-weight: bold;
            text-transform: uppercase;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        tr:hover {
            background-color: #f1f1f1;
        }
    </style>
</head>
<body>
    <h1>SonarQube Metrics Report</h1>
    <table>
        <tr>
            <th>Metric</th>
            <th>Value</th>
        </tr>
'''

# Iterate through JSON metrics and append to the table
for measure in data['component']['measures']:
    metric = measure.get('metric', 'N/A')
    value = measure.get('value', 'N/A')
    html_content += f'''
        <tr>
            <td>{metric}</td>
            <td>{value}</td>
        </tr>
    '''

html_content += '''
    </table>
</body>
</html>
'''

# Write the final HTML report to the desired file path
with open('/jenkins/workspace/archive/metrics_report.html', 'w') as f:
    f.write(html_content)
"""
    
                        // Write the Python script dynamically to a file
                        writeFile file: 'generate_report.py', text: pythonScript
    
                        // Run the Python script to generate the HTML report
                        sh 'python3 generate_report.py'
                        echo "HTML report successfully generated at /jenkins/workspace/archive/metrics_report.html"
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
            script {
                echo "Publishing Metrics Report..."
                publishHTML([
                    reportName: "SonarQube Metrics Report ${env.BUILD_NUMBER}",
                    reportDir: '/jenkins/workspace/archive/',
                    reportFiles: 'metrics_report.html',
                    keepAll: true,
                    allowMissing: false,
                    alwaysLinkToLastBuild: true
                ])
            }
        }
    }
}

