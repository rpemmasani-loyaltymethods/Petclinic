pipeline {
    agent any

    environment {
        MAVEN_HOME = tool name: 'maven3'
    }

    stages {
        stage('Git Checkout') {
            steps {
                git branch: "${env.BRANCH_NAME}", changelog: false, poll: false, url: 'https://github.com/rpemmasani-loyaltymethods/Petclinic.git'
                echo "The branch name is: ${env.BRANCH_NAME}"
            }
        }

        stage('Test & Coverage') {
            steps {
                sh 'mvn clean verify'
            }
        }

        stage('Publish JaCoCo HTML Report') {
            steps {
                publishHTML([ 
                    reportDir: 'target/site/jacoco',
                    reportFiles: 'index.html',
                    reportName: 'JaCoCo Coverage Report',
                    keepAll: true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: false
                ])
            }
        }

        stage('Set Build Description with Coverage Summary') {
            steps {
                script {
                    def summary = ""
                    def xmlPath = "target/site/jacoco/jacoco.xml"

                    if (fileExists(xmlPath)) {
                        def xmlContent = readFile(xmlPath)

                        def extractCoverage = { type ->
                            def matcher = xmlContent =~ /<counter type="${type}" missed="(\d+)" covered="(\d+)"\/>/
                            if (matcher.find()) {
                                def missed = matcher.group(1).toInteger()
                                def covered = matcher.group(2).toInteger()
                                def total = missed + covered
                                def percent = total > 0 ? (100.0 * covered / total) : 0.0
                                return String.format("%.1f", percent)
                            } else {
                                return "0.0"
                            }
                        }

                        def pctMethods = extractCoverage("METHOD")
                        def pctBranches = extractCoverage("BRANCH")
                        def pctLines = extractCoverage("LINE")

                        summary = """
                <h3 style="margin-bottom:8px;">Code Coverage</h3>

                <b>Methods</b><br/>
                <div style="width:300px;height:24px;background:#eee;display:flex;font-weight:bold;font-size:13px;">
                <div style="width:${pctMethods}%;background:limegreen;color:#222;text-align:right;padding-right:4px;">
                    ${pctMethods}%
                </div>
                <div style="width:${100 - pctMethods.toFloat()}%;background:#c00;"></div>
                </div><br/>

                <b>Conditionals (Branches)</b><br/>
                <div style="width:300px;height:24px;background:#eee;display:flex;font-weight:bold;font-size:13px;">
                <div style="width:${pctBranches}%;background:limegreen;color:#222;text-align:right;padding-right:4px;">
                    ${pctBranches}%
                </div>
                <div style="width:${100 - pctBranches.toFloat()}%;background:#c00;"></div>
                </div><br/>

                <b>Statements (Lines)</b><br/>
                <div style="width:300px;height:24px;background:#eee;display:flex;font-weight:bold;font-size:13px;">
                <div style="width:${pctLines}%;background:limegreen;color:#222;text-align:right;padding-right:4px;">
                    ${pctLines}%
                </div>
                <div style="width:${100 - pctLines.toFloat()}%;background:#c00;"></div>
                </div>
                """
                    } else {
                        summary = "⚠️ JaCoCo XML not found."
                    }

                    currentBuild.description = summary
                }
            }
        }
    }
}
