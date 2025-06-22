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
                    def xmlFile = 'target/site/jacoco/jacoco.xml'
                    def summary = ""

                    if (fileExists(xmlFile)) {
                        def xml = readFile(xmlFile)
                        def coverage = new XmlSlurper().parseText(xml)

                        def counters = coverage.counter.collectEntries {
                            [(it.@type.text()): [
                                covered: it.@covered.toInteger(),
                                missed : it.@missed.toInteger()
                            ]]
                        }

                        def calcPct = { type ->
                            def data = counters.get(type, [covered:0, missed:0])
                            def total = data.covered + data.missed
                            return total > 0 ? (100 * data.covered / total) : 0
                        }

                        def summaryPct = { type ->
                            String.format('%.1f', calcPct(type))
                        }

                        def methodPct = summaryPct("METHOD")
                        def condPct   = summaryPct("BRANCH")
                        def stmtPct   = summaryPct("LINE")

                        def methodTotal = counters["METHOD"]?.covered + counters["METHOD"]?.missed ?: 0
                        def methodCovered = counters["METHOD"]?.covered ?: 0

                        summary = """
<h3 style="margin-bottom:8px;">Code Coverage – ${summaryPct("LINE")}% (${methodCovered}/${methodTotal} elements)</h3>

<b>Methods</b><br/>
<div style="width:300px;height:24px;background:#eee;display:flex;font-weight:bold;font-size:13px;">
  <div style="width:${methodPct}%;background:limegreen;color:#222;text-align:right;padding-right:4px;">
    ${methodPct}%
  </div>
  <div style="width:${100 - methodPct}%;background:#c00;"></div>
</div><br/>

<b>Conditionals (Branches)</b><br/>
<div style="width:300px;height:24px;background:#eee;display:flex;font-weight:bold;font-size:13px;">
  <div style="width:${condPct}%;background:limegreen;color:#222;text-align:right;padding-right:4px;">
    ${condPct}%
  </div>
  <div style="width:${100 - condPct}%;background:#c00;"></div>
</div><br/>

<b>Statements (Lines)</b><br/>
<div style="width:300px;height:24px;background:#eee;display:flex;font-weight:bold;font-size:13px;">
  <div style="width:${stmtPct}%;background:limegreen;color:#222;text-align:right;padding-right:4px;">
    ${stmtPct}%
  </div>
  <div style="width:${100 - stmtPct}%;background:#c00;"></div>
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
