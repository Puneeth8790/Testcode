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
        // 1. DECLARATIVE TOOL INSTALL
        // =========================================================

        stage('1. Declarative Tool Install') {
            steps {

                echo "=========================================="
                echo "Tool Configuration"
                echo "=========================================="

                sh '''
                    echo "Java version:"
                    java -version

                    echo "Python version:"
                    python3 --version

                    echo "Node version:"
                    node --version || true

                    echo "NPM version:"
                    npm --version || true

                    echo "Trivy version:"
                    trivy --version || true
                '''
            }
        }


        // =========================================================
        // 2. CLEAN WORKSPACE
        // =========================================================

        stage('2. Clean Workspace') {
            steps {

                echo "=========================================="
                echo "Cleaning Jenkins Workspace"
                echo "=========================================="

                deleteDir()

                echo "Workspace cleaned successfully"
            }
        }


        // =========================================================
        // 3. GIT CHECKOUT
        // =========================================================

        stage('3. Git Checkout') {
            steps {

                echo "=========================================="
                echo "Checking out Test Code"
                echo "=========================================="

                git(
                    branch: "${TARGET_BRANCH}",
                    url: "${REPO_URL}"
                )

                echo "Git checkout completed successfully"
            }
        }


        // =========================================================
        // 4. SONARQUBE ANALYSIS
        // =========================================================

        stage('4. SonarQube Analysis') {
            steps {

                echo "=========================================="
                echo "SonarQube Analysis / SAST"
                echo "=========================================="

                withSonarQubeEnv("${SONAR_SERVER}") {

                    withCredentials([
                        string(
                            credentialsId: "${SONAR_TOKEN_CREDENTIAL}",
                            variable: 'SONAR_AUTH_TOKEN'
                        )
                    ]) {

                        sh '''
                            set -e

                            echo "SonarQube URL:"
                            echo "$SONAR_HOST_URL"

                            echo "Checking SonarScanner..."

                            "$SCANNER_HOME/bin/sonar-scanner" --version

                            if [ ! -f coverage.xml ]; then

                                echo "coverage.xml does not exist yet."
                                echo "Unit tests and coverage will run after SonarQube."

                            fi

                            echo "Starting SonarQube Analysis..."

                            "$SCANNER_HOME/bin/sonar-scanner" \
                                -Dsonar.projectName="$SONAR_PROJECT_NAME" \
                                -Dsonar.projectKey="$SONAR_PROJECT_KEY" \
                                -Dsonar.sources=app \
                                -Dsonar.tests=tests \
                                -Dsonar.host.url="$SONAR_HOST_URL" \
                                -Dsonar.token="$SONAR_AUTH_TOKEN"

                            echo "=========================================="
                            echo "SonarQube Analysis Completed"
                            echo "=========================================="
                        '''
                    }
                }
            }
        }


        // =========================================================
        // 5. CODE QUALITY GATE
        // =========================================================

        stage('5. Code Quality Gate') {
            steps {

                echo "=========================================="
                echo "SonarQube Code Quality Gate"
                echo "=========================================="

                timeout(time: 5, unit: 'MINUTES') {

                    waitForQualityGate(
                        abortPipeline: true
                    )
                }

                echo "=========================================="
                echo "SonarQube Quality Gate PASSED"
                echo "=========================================="
            }
        }


        // =========================================================
        // 6. INSTALL NPM DEPENDENCIES
        // =========================================================

        stage('6. Install NPM Dependencies') {
            steps {

                echo "=========================================="
                echo "Installing Frontend NPM Dependencies"
                echo "=========================================="

                sh '''
                    set -e

                    if [ -f frontend/package.json ]; then

                        echo "Frontend package.json found"

                        cd frontend

                        echo "Node version:"
                        node --version

                        echo "NPM version:"
                        npm --version

                        echo "Installing dependencies..."

                        if [ -f package-lock.json ]; then
                            npm ci
                        else
                            npm install
                        fi

                        echo "NPM dependencies installed successfully"

                    else

                        echo "frontend/package.json not found"
                        echo "Skipping NPM dependency installation"

                    fi
                '''
            }
        }


        // =========================================================
        // 7. UNIT TEST & CODE COVERAGE
        // =========================================================

        stage('7. Unit Test & Code Coverage') {
            steps {

                sh '''
                    set -e

                    echo "=========================================="
                    echo "Python Unit Tests & Code Coverage"
                    echo "=========================================="

                    python3 --version

                    echo "Installing Python dependencies..."

                    python3 -m pip install --user -r requirements.txt

                    echo "Running unit tests..."

                    python3 -m pytest \
                        tests/ \
                        --cov=app \
                        --cov-report=term-missing \
                        --cov-report=xml:coverage.xml \
                        --cov-report=html:htmlcov

                    if [ ! -f coverage.xml ]; then
                        echo "ERROR: coverage.xml was not generated"
                        exit 1
                    fi

                    echo "Code coverage completed successfully"
                '''

                archiveArtifacts(
                    artifacts: 'coverage.xml,htmlcov/**',
                    allowEmptyArchive: false
                )
            }
        }


        // =========================================================
        // 8. PYTHON DEPENDENCY VULNERABILITY SCAN
        // =========================================================

        stage('8. Dependency Vulnerability Scan') {
            steps {

                sh '''
                    set -e

                    echo "=========================================="
                    echo "Python Dependency Vulnerability Scan"
                    echo "=========================================="

                    python3 -m pip install --user --upgrade pip-audit

                    python3 -m pip_audit --version

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

                            echo "Retrying in 10 seconds..."
                            sleep 10

                        fi

                    done

                    if [ ! -f pip-audit-report.json ]; then
                        echo "ERROR: pip-audit report was not generated"
                        exit 1
                    fi

                    echo "Dependency vulnerability scan completed"
                '''

                archiveArtifacts(
                    artifacts: 'pip-audit-report.json',
                    allowEmptyArchive: false
                )
            }
        }


        // =========================================================
        // 9. OWASP FILESYSTEM SCAN
        // =========================================================

        stage('9. OWASP FS Scan') {
            steps {

                echo "=========================================="
                echo "OWASP Filesystem Dependency Scan"
                echo "=========================================="

                sh '''
                    set -e

                    if ! command -v dependency-check.sh >/dev/null 2>&1; then

                        echo "ERROR: OWASP Dependency-Check is not installed."
                        echo "Please configure dependency-check on the Jenkins agent."

                        exit 1
                    fi

                    dependency-check.sh \
                        --project "Test-Code" \
                        --scan . \
                        --format HTML \
                        --format JSON \
                        --out dependency-check-report

                    echo "OWASP Dependency-Check completed"

                    ls -lh dependency-check-report/
                '''

                archiveArtifacts(
                    artifacts: 'dependency-check-report/**',
                    allowEmptyArchive: false
                )
            }
        }


        // =========================================================
        // 10. TRIVY FILE SCAN
        // =========================================================

        stage('10. Trivy File Scan') {
            steps {

                echo "=========================================="
                echo "Trivy Filesystem Security Scan"
                echo "=========================================="

                sh '''
                    set -e

                    if ! command -v trivy >/dev/null 2>&1; then
                        echo "ERROR: Trivy is not installed on Jenkins agent."
                        exit 1
                    fi

                    echo "Trivy version:"
                    trivy --version

                    echo "=========================================="
                    echo "Running Trivy Filesystem Scan"
                    echo "=========================================="

                    trivy fs \
                        --scanners vuln,secret,misconfig \
                        --severity HIGH,CRITICAL \
                        --format table \
                        .

                    echo "=========================================="
                    echo "Generating Trivy JSON Report"
                    echo "=========================================="

                    trivy fs \
                        --scanners vuln,secret,misconfig \
                        --severity HIGH,CRITICAL \
                        --format json \
                        --output trivy-report.json \
                        .

                    if [ ! -f trivy-report.json ]; then
                        echo "ERROR: Trivy report was not generated"
                        exit 1
                    fi

                    echo "Trivy filesystem scan completed"
                '''

                archiveArtifacts(
                    artifacts: 'trivy-report.json',
                    allowEmptyArchive: false
                )
            }
        }
    }


    // =============================================================
    // POST BUILD
    // =============================================================

    post {

        success {

            echo "=========================================="
            echo "TEST CODE PIPELINE SUCCESS"
            echo "=========================================="

            echo "1. Tool Installation       : PASSED"
            echo "2. Clean Workspace         : PASSED"
            echo "3. Git Checkout            : PASSED"
            echo "4. SonarQube Analysis      : PASSED"
            echo "5. Code Quality Gate       : PASSED"
            echo "6. NPM Dependencies        : PASSED"
            echo "7. Unit Tests & Coverage   : PASSED"
            echo "8. Dependency Scan         : PASSED"
            echo "9. OWASP FS Scan           : PASSED"
            echo "10. Trivy File Scan        : PASSED"

            echo "=========================================="
        }

        failure {

            echo "=========================================="
            echo "TEST CODE PIPELINE FAILED"
            echo "=========================================="

            echo "Please check the Jenkins console output."

            echo "Possible areas:"
            echo "1. Git checkout"
            echo "2. Unit tests"
            echo "3. Code coverage"
            echo "4. SonarQube analysis"
            echo "5. SonarQube quality gate"
            echo "6. NPM dependencies"
            echo "7. pip-audit"
            echo "8. OWASP Dependency-Check"
            echo "9. Trivy security scan"

            echo "=========================================="
        }
    }
}
