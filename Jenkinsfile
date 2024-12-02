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

                // Use a multi-line string with proper indentation
                sh '''
                    python3 -c "
import json
import sys
# Read the JSON file
with open('sonar_status.json', 'r') as f:
    data = json.load(f)

# Extract relevant information from the JSON
sonarStatus = data.get('projectStatus', {}).get('status', 'Unknown')
print(sonarStatus)

# Check if the quality gate failed
if sonarStatus != 'OK':
    print('Quality Gate failed! SonarQube status: {}'.format(sonarStatus))
    sys.exit(1)  # Exit with status code 1 to fail the pipeline
                    "
                '''
            }
        }
    }
}

