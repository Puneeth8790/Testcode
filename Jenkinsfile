pipeline {

    agent any

    triggers {
        githubPush()
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {

        REPO_URL = "https://github.com/Puneeth8790/Testcode.git"
        TARGET_BRANCH = "feature"

        // SonarQube
        SCANNER_HOME = tool 'sonar-scanner'
        SONAR_SERVER = "sonar-server"
        SONAR_TOKEN_CREDENTIAL = "sonar-test"

        SONAR_PROJECT_NAME = "Test Code"
        SONAR_PROJECT_KEY = "Test-Code"
    }

    stages {

        // =========================================================
        // 1. CHECKOUT
        // =========================================================

        stage('1. GitHub Checkout') {
            steps {

                echo "=========================================="
                echo "Checking out Test Code"
                echo "=========================================="

                git(
                    branch: "${TARGET_BRANCH}",
                    url: "${REPO_URL}"
                )
            }
        }


        // =========================================================
        // 2. UNIT TEST + CODE COVERAGE
        // =========================================================

        stage('2. Unit Test & Code Coverage') {
            steps {

                sh '''
                    set -e

                    echo "=========================================="
                    echo "Python Environment"
                    echo "=========================================="

                    python3 --version

                    echo "Installing Python dependencies..."

                    python3 -m pip install --user -r requirements.txt

                    echo "Checking FastAPI..."

                    python3 -c "import fastapi; print('FastAPI installed successfully')"

                    echo "=========================================="
                    echo "Running Unit Tests"
                    echo "=========================================="

                    python3 -m pytest \
                        tests/ \
                        --cov=app \
                        --cov-report=term-missing \
                        --cov-report=xml:coverage.xml \
                        --cov-report=html:htmlcov

                    echo "=========================================="
                    echo "Checking coverage.xml"
                    echo "=========================================="

                    if [ ! -f coverage.xml ]; then
                        echo "ERROR: coverage.xml was not generated"
                        exit 1
                    fi

                    echo "Coverage file generated successfully"
                '''

                archiveArtifacts(
                    artifacts: 'coverage.xml,htmlcov/**',
                    allowEmptyArchive: false
                )
            }
        }


       stage('3. Dependency Vulnerability Scan') {
    steps {
        sh '''
            set -e

            echo "=========================================="
            echo "Python Dependency Vulnerability Scan"
            echo "=========================================="

            echo "Installing pip-audit..."

            python3 -m pip install --user --upgrade pip-audit

            echo "Checking pip-audit version..."

            python3 -m pip_audit --version

            echo "Running dependency vulnerability scan..."

            # Retry the scan because the vulnerability
            # database is queried over the internet.
            for i in 1 2 3; do

                echo "pip-audit attempt: $i"

                if python3 -m pip_audit \
                    -r requirements.txt \
                    -f json \
                    -o pip-audit-report.json; then

                    echo "pip-audit completed successfully"
                    break

                else

                    if [ "$i" -eq 3 ]; then
                        echo "ERROR: pip-audit failed after 3 attempts"
                        exit 1
                    fi

                    echo "pip-audit failed. Retrying in 10 seconds..."
                    sleep 10

                fi

            done

            echo "=========================================="
            echo "Dependency Vulnerability Scan Completed"
            echo "=========================================="

            if [ ! -f pip-audit-report.json ]; then
                echo "ERROR: pip-audit report was not generated"
                exit 1
            fi

            echo "Security report generated:"
            ls -lh pip-audit-report.json
        '''

        archiveArtifacts(
            artifacts: 'pip-audit-report.json',
            allowEmptyArchive: false
        )
    }
}


        // =========================================================
        // 4. TRIVY SECURITY SCAN
        // =========================================================

        stage('4. Trivy Security Scan') {
            steps {

                sh '''
                    set -e

                    echo "=========================================="
                    echo "Trivy Security Scan"
                    echo "=========================================="

                    if ! command -v trivy >/dev/null 2>&1; then
                        echo "ERROR: Trivy is not installed on Jenkins agent."
                        echo "Please install Trivy on the Jenkins agent."
                        exit 1
                    fi

                    echo "Trivy version:"
                    trivy --version

                    echo "=========================================="
                    echo "Scanning Application Filesystem"
                    echo "=========================================="

                    trivy fs \
                        --scanners vuln,secret,misconfig \
                        --severity HIGH,CRITICAL \
                        --format table \
                        .

                    echo "=========================================="
                    echo "Generating JSON Security Report"
                    echo "=========================================="

                    trivy fs \
                        --scanners vuln,secret,misconfig \
                        --severity HIGH,CRITICAL \
                        --format json \
                        --output trivy-report.json \
                        .

                    echo "=========================================="
                    echo "Trivy scan completed"
                    echo "=========================================="

                    if [ ! -f trivy-report.json ]; then
                        echo "ERROR: Trivy report was not generated"
                        exit 1
                    fi
                '''

                archiveArtifacts(
                    artifacts: 'trivy-report.json',
                    allowEmptyArchive: true
                )
            }
        }


        // =========================================================
        // 5. SONARQUBE ANALYSIS
        // =========================================================

        stage('5. SonarQube Analysis - Test Code') {
            steps {

                withSonarQubeEnv("${SONAR_SERVER}") {

                    withCredentials([
                        string(
                            credentialsId: "${SONAR_TOKEN_CREDENTIAL}",
                            variable: 'SONAR_AUTH_TOKEN'
                        )
                    ]) {

                        sh '''
                            set -e

                            echo "=========================================="
                            echo "SonarQube Analysis"
                            echo "Project: $SONAR_PROJECT_NAME"
                            echo "Key: $SONAR_PROJECT_KEY"
                            echo "Branch checked out: $TARGET_BRANCH"
                            echo "=========================================="

                            echo "SonarQube URL:"
                            echo "$SONAR_HOST_URL"

                            echo "Checking scanner..."

                            "$SCANNER_HOME/bin/sonar-scanner" --version

                            if [ ! -f coverage.xml ]; then
                                echo "ERROR: coverage.xml not found"
                                exit 1
                            fi

                            echo "Starting SonarQube scan..."

                            "$SCANNER_HOME/bin/sonar-scanner" \
                                -Dsonar.projectName="$SONAR_PROJECT_NAME" \
                                -Dsonar.projectKey="$SONAR_PROJECT_KEY" \
                                -Dsonar.sources=app \
                                -Dsonar.tests=tests \
                                -Dsonar.host.url="$SONAR_HOST_URL" \
                                -Dsonar.token="$SONAR_AUTH_TOKEN" \
                                -Dsonar.python.coverage.reportPaths=coverage.xml

                            echo "=========================================="
                            echo "SonarQube scan completed successfully"
                            echo "=========================================="
                        '''
                    }
                }
            }
        }


        // =========================================================
        // 6. SONARQUBE QUALITY GATE
        // =========================================================

        stage('6. SonarQube Quality Gate') {
            steps {

                timeout(time: 5, unit: 'MINUTES') {

                    waitForQualityGate(
                        abortPipeline: true
                    )
                }
            }
        }
    }


    // =============================================================
    // POST BUILD
    // =============================================================

    post {

        success {

            echo "=========================================="
            echo "Test Code Pipeline SUCCESS"
            echo "=========================================="

            echo "Security scans completed."
            echo "SonarQube Quality Gate passed."
            echo "Unit tests and code coverage completed."
        }

        failure {

            echo "=========================================="
            echo "Test Code Pipeline FAILED"
            echo "=========================================="

            echo "Check Jenkins console output."
            echo "Review:"
            echo "1. Unit test results"
            echo "2. pip-audit dependency vulnerabilities"
            echo "3. Trivy security vulnerabilities"
            echo "4. SonarQube Quality Gate"
        }
    }
}
