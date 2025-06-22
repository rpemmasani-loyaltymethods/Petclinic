pipeline {
    agent any

    environment {
        MAVEN_HOME = tool name: 'maven3'
    }

    stages {
        stage('Git Checkout') {
            steps {
                git branch: "${env.BRANCH_NAME}", changelog: false, poll: false, url: 'https://github.com/rpemmasani-loyaltymethods/Petclinic.git'
            }
        }

        stage('Build & Test') {
            steps {
                sh 'mvn clean verify'
            }
        }

        stage('Extract Coverage and Render Visual') {
            steps {
                sh '''
                    mkdir -p target/site/jacoco

                    METHOD_MISSED=$(grep 'counter type="METHOD"' target/site/jacoco/jacoco.xml | sed -n 's/.*missed="\\([0-9]*\\)".*/\\1/p')
                    METHOD_COVERED=$(grep 'counter type="METHOD"' target/site/jacoco/jacoco.xml | sed -n 's/.*covered="\\([0-9]*\\)".*/\\1/p')

                    BRANCH_MISSED=$(grep 'counter type="BRANCH"' target/site/jacoco/jacoco.xml | sed -n 's/.*missed="\\([0-9]*\\)".*/\\1/p')
                    BRANCH_COVERED=$(grep 'counter type="BRANCH"' target/site/jacoco/jacoco.xml | sed -n 's/.*covered="\\([0-9]*\\)".*/\\1/p')

                    LINE_MISSED=$(grep 'counter type="LINE"' target/site/jacoco/jacoco.xml | sed -n 's/.*missed="\\([0-9]*\\)".*/\\1/p')
                    LINE_COVERED=$(grep 'counter type="LINE"' target/site/jacoco/jacoco.xml | sed -n 's/.*covered="\\([0-9]*\\)".*/\\1/p')

                    METHOD_TOTAL=$((METHOD_MISSED + METHOD_COVERED))
                    BRANCH_TOTAL=$((BRANCH_MISSED + BRANCH_COVERED))
                    LINE_TOTAL=$((LINE_MISSED + LINE_COVERED))

                    METHOD_PCT=$((METHOD_COVERED * 100 / METHOD_TOTAL))
                    BRANCH_PCT=$((BRANCH_COVERED * 100 / BRANCH_TOTAL))
                    LINE_PCT=$((LINE_COVERED * 100 / LINE_TOTAL))

                    TOTAL_ELEMENTS=$((METHOD_TOTAL + BRANCH_TOTAL + LINE_TOTAL))
                    TOTAL_COVERED=$((METHOD_COVERED + BRANCH_COVERED + LINE_COVERED))
                    TOTAL_PCT=$((TOTAL_COVERED * 100 / TOTAL_ELEMENTS))

                    cat <<EOF > target/site/jacoco/visual.html
<!DOCTYPE html>
<html>
<head>
<style>
    body { font-family: Arial, sans-serif; }
    .bar { height: 20px; width: 300px; display: flex; margin-bottom: 10px; }
    .green { background: limegreen; height: 100%; }
    .red { background: red; height: 100%; }
</style>
</head>
<body>
<h3>Code Coverage – ${TOTAL_PCT}% (${TOTAL_COVERED}/${TOTAL_ELEMENTS} elements)</h3>

<b>Methods (${METHOD_PCT}%)</b>
<div class="bar">
  <div class="green" style="width: ${METHOD_PCT}%;"></div>
  <div class="red" style="width: $((100 - METHOD_PCT))%;"></div>
</div>

<b>Conditionals (${BRANCH_PCT}%)</b>
<div class="bar">
  <div class="green" style="width: ${BRANCH_PCT}%;"></div>
  <div class="red" style="width: $((100 - BRANCH_PCT))%;"></div>
</div>

<b>Statements (${LINE_PCT}%)</b>
<div class="bar">
  <div class="green" style="width: ${LINE_PCT}%;"></div>
  <div class="red" style="width: $((100 - LINE_PCT))%;"></div>
</div>
</body>
</html>
EOF
                '''
            }
        }

        stage('Publish Visual & Full Report') {
            steps {
                publishHTML([
                    reportDir: 'target/site/jacoco',
                    reportFiles: 'visual.html',
                    reportName: 'Coverage Summary Visual',
                    keepAll: true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: false
                ])

                publishHTML([
                    reportDir: 'target/site/jacoco',
                    reportFiles: 'index.html',
                    reportName: 'JaCoCo Full Report',
                    keepAll: true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: false
                ])
            }
        }
    }
}
