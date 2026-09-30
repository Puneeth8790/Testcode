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

        // GITHUB
        REPO_URL      = "https://github.com/Puneeth8790/Testcode.git"
        TARGET_BRANCH = "feature"

        // SONARQUBE
        SCANNER_HOME       = tool 'sonar-scanner'
        SONAR_PROJECT_NAME = "Testing Code"
        SONAR_PROJECT_KEY  = "Test-Code"

        // Jenkins -> Manage Jenkins -> System -> SonarQube servers
        SONAR_SERVER       = "sonar-server"

        // Jenkins -> Credentials (Secret text)
        SONAR_TOKEN_ID     = "sonar-token"

        // PYTHON
        VENV_DIR           = ".venv"
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

                echo "=========================================="
                echo "GitHub Checkout"
                echo "=========================================="

                echo "Repository : ${REPO_URL}"
                echo "Branch     : ${TARGET_BRANCH}"

                git(
                    branch: "${TARGET_BRANCH}",
                    url: "${REPO_URL}"
                )

                echo "GitHub Checkout Completed Successfully"

                sh '''
                    pwd

                    echo ""
                    echo "Root files:"
                    ls -la

                    echo ""
                    echo "Application directory:"
                    ls -la app || true

                    echo ""
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

                echo "=========================================="
                echo "Python Unit Tests + Code Coverage"
                echo "=========================================="

                sh '''
                    set -e

                    echo "Python Version"
                    python3 --version

                    echo ""
                    echo "=========================================="
                    echo "Checking Required Files"
                    echo "=========================================="

                    if [ ! -f requirements.txt ]; then
                        echo "ERROR: requirements.txt not found."
                        exit 1
                    fi

                    if [ ! -d app ]; then
                        echo "ERROR: app directory not found."
                        exit 1
                    fi

                    if [ ! -d tests ]; then
                        echo "ERROR: tests directory not found."
                        exit 1
                    fi

                    if [ ! -f .coveragerc ]; then
                        echo "WARNING: .coveragerc not found."
                        echo "Sonar may report 0% coverage due to path mismatch."
                        echo "Add .coveragerc with: relative_files = True"
                    fi

                    # Remove old reports so stale files cannot hide a failure
                    rm -rf coverage.xml htmlcov .coverage

                    echo ""
                    echo "=========================================="
                    echo "Creating Virtual Environment"
                    echo "=========================================="

                    # Requires: sudo apt install python3-venv
                    python3 -m venv "$VENV_DIR"
                    . "$VENV_DIR/bin/activate"

                    echo ""
                    echo "=========================================="
                    echo "Installing Dependencies"
                    echo "=========================================="

                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest pytest-cov

                    python -c "import fastapi; print('FastAPI version:', fastapi.__version__)"

                    echo ""
                    echo "=========================================="
                    echo "Application Files"
                    echo "=========================================="

                    find app -maxdepth 2 -type f | sort

                    echo ""
                    echo "=========================================="
                    echo "Test Files"
                    echo "=========================================="

                    TEST_FILES=$(find tests -type f \\( \
                        -name "test_*.py" \
                        -o -name "*_test.py" \
                    \\) | sort)

                    if [ -z "$TEST_FILES" ]; then
                        echo "ERROR: No Python test files found."
                        exit 1
                    fi

                    echo "Test files found:"
                    echo "$TEST_FILES"

                    echo ""
                    echo "=========================================="
                    echo "Running Unit Tests"
                    echo "=========================================="

                    python -m pytest \
                        tests/ \
                        --cov=app \
                        --cov-report=term-missing \
                        --cov-report=xml:coverage.xml \
                        --cov-report=html:htmlcov

                    echo ""
                    echo "=========================================="
                    echo "Checking Coverage Reports"
                    echo "=========================================="

                    if [ ! -f coverage.xml ]; then
                        echo "ERROR: coverage.xml was not generated."
                        exit 1
                    fi

                    if [ ! -d htmlcov ]; then
                        echo "ERROR: htmlcov directory was not generated."
                        exit 1
                    fi

                    ls -lh coverage.xml
                    ls -ld htmlcov

                    echo "CODE COVERAGE COMPLETED"
                '''

                archiveArtifacts(
                    artifacts: 'coverage.xml,htmlcov/**',
                    allowEmptyArchive: false
                )
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
                    withCredentials([
                        string(
                            credentialsId: "${SONAR_TOKEN_ID}",
                            variable: 'SONAR_TOKEN'
                        )
                    ]) {

                        sh '''
                            set -e

                            echo "=========================================="
                            echo "SonarQube Analysis"
                            echo "=========================================="

                            echo "Project Name : $SONAR_PROJECT_NAME"
                            echo "Project Key  : $SONAR_PROJECT_KEY"
                            echo "Source       : app"
                            echo "Tests        : tests"

                            if [ ! -f coverage.xml ]; then
                                echo "ERROR: coverage.xml not found."
                                exit 1
                            fi

                            ls -lh coverage.xml

                            if [ ! -f "$SCANNER_HOME/bin/sonar-scanner" ]; then
                                echo "ERROR: SonarScanner not found."
                                echo "SCANNER_HOME=$SCANNER_HOME"
                                exit 1
                            fi

                            "$SCANNER_HOME/bin/sonar-scanner" --version

                            echo ""
                            echo "Running SonarQube Scanner"

                            "$SCANNER_HOME/bin/sonar-scanner" \
                                -Dsonar.projectName="$SONAR_PROJECT_NAME" \
                                -Dsonar.projectKey="$SONAR_PROJECT_KEY" \
                                -Dsonar.sources=app \
                                -Dsonar.tests=tests \
                                -Dsonar.host.url="$SONAR_HOST_URL" \
                                -Dsonar.python.coverage.reportPaths=coverage.xml \
                                -Dsonar.coverage.exclusions="tests/**,**/__init__.py"

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

                echo "Waiting for SonarQube Quality Gate"

                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }

                echo "SONARQUBE QUALITY GATE PASSED"
            }
        }
    }

    // ============================================================
    // POST ACTIONS
    // ============================================================
    post {

        success {

            echo """
            ==========================================
                 JENKINS PIPELINE SUCCESS
            ==========================================

            Repository      : ${REPO_URL}
            Branch          : ${TARGET_BRANCH}

            SonarQube Project : ${SONAR_PROJECT_NAME}
            SonarQube Key     : ${SONAR_PROJECT_KEY}

            Unit Tests      : PASSED
            Code Coverage   : GENERATED
            SonarQube Scan  : PASSED
            Quality Gate    : PASSED

            ==========================================
            """
        }

        failure {

            echo """
            ==========================================
                 JENKINS PIPELINE FAILED
            ==========================================

            Repository : ${REPO_URL}
            Branch     : ${TARGET_BRANCH}

            Please check the failed stage
            in Jenkins Console Output.

            ==========================================
            """
        }

        always {
            // Requires the "Workspace Cleanup" plugin.
            // Reports are already archived. Remove this if the plugin is missing.
            cleanWs()
        }
    }
}
