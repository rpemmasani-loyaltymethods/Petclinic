pipeline {
    agent any

    parameters {
        string(name: 'SONAR_PROJECT_KEY',  defaultValue: 'Petclinic')
        string(name: 'SONAR_PROJECT_NAME', defaultValue: 'Petclinic')
        choice(name: 'QUALITY_GATE',
               choices: ['Sonar way','Default-Quality-Gate','Main-Quality-Gate','Feature-Quality-Gate'])
    }

    environment {
        MAVEN_HOME     = tool(name: 'maven3')
        SONAR_INSTANCE = 'Sonarqube-8.9.2'          // name of Jenkins global config
        SONAR_URL      = 'https://sonarqube.devops.lmvi.net'
        SONAR_TOKEN    = credentials('SONARQUBE_TOKEN')
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: "${env.BRANCH_NAME}",
                    url: 'https://github.com/rpemmasani-loyaltymethods/Petclinic.git'
            }
        }

        /* 1️⃣  compile, test & produce JaCoCo -------------------------------------------------------------------------------- */
        stage('Build & Unit-Test') {
            steps { sh 'mvn --batch-mode clean verify' }
        }

        /* 2️⃣  Sonar analysis (so metrics JSON really exists) ----------------------------------------------------------------- */
        stage('SonarQube Scan') {
            steps {
                withSonarQubeEnv('Sonarqube-8.9.2') {
                    sh """
                       mvn --batch-mode sonar:sonar \
                           -Dsonar.projectKey=${params.SONAR_PROJECT_KEY} \
                           -Dsonar.projectName=${params.SONAR_PROJECT_NAME} \
                           -Dsonar.login=$SONAR_TOKEN
                       """
                }
            }
        }

        /* 3️⃣  wait for the background quality-gate to finish (optional, but nicer) ------------------------------------------- */
        stage('Await Quality Gate') {
            steps { timeout(time: 5, unit: 'MINUTES') { waitForQualityGate abortPipeline: false } }
        }

        /* 4️⃣  Fetch Sonar metrics & build HTML snip --------------------------------------------------------------------------- */
        stage('Fetch Metrics & Build Snippet') {
            steps {
                script {
                    sh 'mkdir -p archive'

                    def metricsURL  = "${SONAR_URL}/api/measures/component" +
                                       "?component=${params.SONAR_PROJECT_KEY}" +
                                       "&metricKeys=coverage,line_coverage,branch_coverage,lines_to_cover,uncovered_lines"

                    sh """
                       curl -s -u ${SONAR_TOKEN}: ${metricsURL} > archive/sonar_metrics.json
                       """

                    /* ---------- build little green/red widget (or fall back to JaCoCo) ---------- */
                    def cov = [line:0, branch:0, covered:0, total:0]

                    if (fileExists('archive/sonar_metrics.json')) {
                        def j = readJSON file:'archive/sonar_metrics.json'
                        def m = j.component.measures.collectEntries{ [(it.metric): it.value] }
                        cov.line    = m.line_coverage?.toFloat()    ?: 0
                        cov.branch  = m.branch_coverage?.toFloat()  ?: 0
                        cov.total   = m.lines_to_cover?.toInteger() ?: 0
                        cov.covered = cov.total - (m.uncovered_lines?.toInteger() ?: 0)
                    }

                    /* fallback to JaCoCo XML if Sonar failed */
                    if (cov.total == 0 && fileExists('target/site/jacoco/jacoco.xml')) {
                        def xml  = readFile('target/site/jacoco/jacoco.xml')
                        def line = xml =~ /<counter type="LINE" missed="(\d+)" covered="(\d+)"/
                        def branch = xml =~ /<counter type="BRANCH" missed="(\d+)" covered="(\d+)"/
                        if (line) {
                            cov.covered = line[0][2].toInteger()
                            def missed  = line[0][1].toInteger()
                            cov.total   = cov.covered + missed
                            cov.line    = 100*cov.covered / cov.total
                        }
                        if (branch) {
                            def brCov  = branch[0][2].toInteger()
                            def brMiss = branch[0][1].toInteger()
                            cov.branch = 100*brCov / (brCov + brMiss)
                        }
                    }

                    /* build the HTML block */
                    currentBuild.description = """
<h3>Code Coverage – ${String.format('%.1f', cov.line)} % (${cov.covered}/${cov.total} lines)</h3>

<b>Conditionals (Branches)</b><br/>
<div style="width:300px;height:24px;background:#eee;display:flex;">
  <div style="width:${cov.branch}%;background:limegreen;text-align:right;color:#222;font-weight:bold;">
    ${String.format('%.1f', cov.branch)}%
  </div><div style="width:${100-cov.branch}%;background:#c00;"></div>
</div><br/>

<b>Statements (Lines)</b><br/>
<div style="width:300px;height:24px;background:#eee;display:flex;">
  <div style="width:${cov.line}%;background:limegreen;text-align:right;color:#222;font-weight:bold;">
    ${String.format('%.1f', cov.line)}%
  </div><div style="width:${100-cov.line}%;background:#c00;"></div>
</div>
"""
                }
            }
        }

        /* 5️⃣  Publish full reports (JaCoCo & Cobertura) ---------------------------------------------------------------------- */
        stage('Publish JaCoCo HTML') {
            steps {
                publishHTML([
                    reportDir           : 'target/site/jacoco',
                    reportFiles         : 'index.html',
                    reportName          : 'JaCoCo Coverage',
                    keepAll             : true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: false
                ])
            }
        }

        stage('Publish Cobertura') {
            steps {
                cobertura coberturaReportFile: 'archive/sonar_cobertura.xml',
                         failOnError       : false,
                         failNoReports     : false,
                         autoUpdateHealth  : false,
                         autoUpdateStability: false
            }
        }
    }

    post {
        always {
            /* still try to publish your combined Sonar HTML if it exists */
            script {
                if (fileExists('archive/combined_metrics_report.html')) {
                    publishHTML target: [
                        reportDir: 'archive',
                        reportFiles: 'combined_metrics_report.html',
                        reportName: 'SonarQube Combined Report',
                        keepAll: true,
                        alwaysLinkToLastBuild: true,
                        allowMissing: false
                    ]
                }
            }
        }
    }
}
