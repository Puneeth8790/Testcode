pipeline {

    agent any

    // ============================================================
    // TRIGGERS
    // ============================================================
    // Use ONE trigger. githubPush() needs a GitHub webhook pointing to
    // http://<jenkins-url>/github-webhook/. If you have no webhook,
    // comment it out and enable pollSCM instead.
    triggers {
        githubPush()
        // pollSCM('H/5 * * * *')
    }

    // ============================================================
    // OPTIONS
    // ============================================================
    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 30, unit: 'MINUTES')
    }

    // ============================================================
    // ENVIRONMENT
    // ============================================================
    environment {
        REPO_URL       = "https://github.com/Puneeth8790/Testcode.git"
        TARGET_BRANCH  = "feature"

        // Jenkins -> Manage Jenkins -> Tools
        SCANNER_HOME   = tool 'sonar-scanner'

        // Jenkins -> Manage Jenkins -> System -> SonarQube servers
        SONAR_SERVER   = "sonar-server"

        // Jenkins -> Credentials (Secret text)
        SONAR_TOKEN_ID = "sonar-token"

        VENV_DIR       = ".venv"
    }

    // ============================================================
    // STAGES
    // ============================================================
    stages {

        // ============================================================
        // 1. GITHUB CHECKOUT
        // ============================================================
        stage('1. GitHub Checkout') {
            steps {
                echo "Repository : ${REPO_URL}"
                echo "Branch     : ${TARGET_BRANCH}"

                git branch: "${TARGET_BRANCH}", url: "${REPO_URL}"

                sh '''
                    pwd
                    echo "Root files:"
                    ls -la
                    echo "Application directory:"
                    ls -la app || true
                    echo "Tests directory:"
                    ls -la tests || true
                '''
            }
        }

        // ============================================================
        // 2. CODE COVERAGE
        // ============================================================
        stage('2. Code Coverage') {
            steps {
                sh '''
                    set -e

                    python3 --version

                    # ---- Required files ----
                    [ -f requirements.txt ] || { echo "ERROR: requirements.txt not found."; exit 1; }
                    [ -d app ]              || { echo "ERROR: app directory not found.";    exit 1; }
                    [ -d tests ]            || { echo "ERROR: tests directory not found.";  exit 1; }

                    if [ ! -f .coveragerc ]; then
                        echo "WARNING: .coveragerc not found. Sonar may report 0% coverage"
                        echo "         due to path mismatch. Add it with relative_files = True."
                    fi

                    # ---- Clean old reports so stale files cannot mask a failure ----
                    rm -rf coverage.xml htmlcov .coverage

                    # ---- Virtual environment (avoids PEP 668 errors) ----
                    # Requires: sudo apt install python3-venv
                    python3 -m venv "$VENV_DIR"
                    . "$VENV_DIR/bin/activate"

                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest pytest-cov

                    python -c "import fastapi; print('FastAPI version:', fastapi.__version__)"

                    # ---- Test files ----
                    TEST_FILES=$(find tests -type f \\( -name "test_*.py" -o -name "*_test.py" \\) | sort)
                    if [ -z "$TEST_FILES" ]; then
                        echo "ERROR: No Python test files found."
                        exit 1
                    fi
                    echo "Test files found:"
                    echo "$TEST_FILES"

                    # ---- Run tests + coverage ----
                    python -m pytest tests/ \
                        --cov=app \
                        --cov-report=term-missing \
                        --cov-report=xml:coverage.xml \
                        --cov-report=html:htmlcov

                    # ---- Verify reports ----
                    [ -f coverage.xml ] || { echo "ERROR: coverage.xml was not generated.";      exit 1; }
                    [ -d htmlcov ]      || { echo "ERROR: htmlcov directory was not generated."; exit 1; }

                    ls -lh coverage.xml
                    echo "CODE COVERAGE COMPLETED"
                '''

                archiveArtifacts artifacts: 'coverage.xml,htmlcov/**', allowEmptyArchive: false
            }
        }

        // ============================================================
        // 3. SONARQUBE ANALYSIS
        // ============================================================
        stage('3. SonarQube Analysis') {
            steps {
                withSonarQubeEnv("${SONAR_SERVER}") {
                    // The scanner reads SONAR_TOKEN automatically, so the
                    // token never appears on the command line.
                    withCredentials([string(credentialsId: "${SONAR_TOKEN_ID}", variable: 'SONAR_TOKEN')]) {
                        sh '''
                            set -e

                            [ -f coverage.xml ] || { echo "ERROR: coverage.xml not found."; exit 1; }
                            [ -f sonar-project.properties ] || { echo "ERROR: sonar-project.properties not found."; exit 1; }
                            [ -x "$SCANNER_HOME/bin/sonar-scanner" ] || { echo "ERROR: SonarScanner not found at $SCANNER_HOME"; exit 1; }

                            "$SCANNER_HOME/bin/sonar-scanner" --version

                            # Project key/name, sources, tests and coverage path
                            # come from sonar-project.properties.
                            "$SCANNER_HOME/bin/sonar-scanner" \
                                -Dsonar.host.url="$SONAR_HOST_URL"

                            echo "SONARQUBE ANALYSIS COMPLETED"
                        '''
                    }
                }
            }
        }

        // ============================================================
        // 4. SONARQUBE QUALITY GATE
        // ============================================================
        // Requires a SonarQube webhook:
        //   Administration -> Configuration -> Webhooks
        //   URL: http://<jenkins-url>/sonarqube-webhook/
        stage('4. SonarQube Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
    }

    // ============================================================
    // POST ACTIONS
    // ============================================================
    post {
        success {
            echo "PIPELINE SUCCESS | ${REPO_URL} | branch: ${TARGET_BRANCH} | Quality Gate: PASSED"
        }
        failure {
            echo "PIPELINE FAILED | ${REPO_URL} | branch: ${TARGET_BRANCH} | Check the failed stage in Console Output."
        }
        always {
            // Requires the "Workspace Cleanup" plugin. Reports are already archived.
            cleanWs()
        }
    }
}
