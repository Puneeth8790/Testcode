pipeline {

    agent any

    triggers {
        githubPush()
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 45, unit: 'MINUTES')
    }

    environment {

        // =========================================================
        // GITHUB
        // =========================================================

        REPO_URL = "https://github.com/Puneeth8790/Testcode.git"
        TARGET_BRANCH = "feature"

        // =========================================================
        // SONARQUBE
        // =========================================================

        SCANNER_HOME = tool 'sonar-scanner'

        SONAR_SERVER = "sonar-server"

        SONAR_TOKEN_CREDENTIAL = "sonar-test"

        SONAR_PROJECT_NAME = "Test Code"
        SONAR_PROJECT_KEY = "Test-Code"
    }


    stages {

        // =========================================================
        // 1. CLEAN WORKSPACE
        // =========================================================

        stage('1. Clean Workspace') {

            steps {

                echo "=========================================="
                echo "Cleaning Jenkins Workspace"
                echo "=========================================="

                deleteDir()

                echo "Workspace cleaned successfully."
            }
        }


        // =========================================================
        // 2. GIT CHECKOUT
        // =========================================================

        stage('2. Git Checkout') {

            steps {

                echo "=========================================="
                echo "Git Checkout"
                echo "=========================================="

                git(
                    branch: "${TARGET_BRANCH}",
                    url: "${REPO_URL}"
                )

                sh '''
                    echo "Current Branch:"
                    git branch --show-current

                    echo ""
                    echo "Latest Commit:"
                    git log -1 --oneline
                '''

                echo "Git checkout completed successfully."
            }
        }


        // =========================================================
        // 3. SONARQUBE ANALYSIS
        // =========================================================

        stage('3. SonarQube Analysis') {

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

                            echo ""
                            echo "SonarScanner Version:"
                            "$SCANNER_HOME/bin/sonar-scanner" --version

                            echo ""
                            echo "Starting SonarQube Analysis..."

                            "$SCANNER_HOME/bin/sonar-scanner" \
                                -Dsonar.projectName="$SONAR_PROJECT_NAME" \
                                -Dsonar.projectKey="$SONAR_PROJECT_KEY" \
                                -Dsonar.sources=app \
                                -Dsonar.tests=tests \
                                -Dsonar.host.url="$SONAR_HOST_URL" \
                                -Dsonar.token="$SONAR_AUTH_TOKEN"

                            echo ""
                            echo "=========================================="
                            echo "SonarQube Analysis Completed"
                            echo "=========================================="
                        '''
                    }
                }
            }
        }


        // =========================================================
        // 4. CODE QUALITY GATE
        // =========================================================

        stage('4. Code Quality Gate') {

            steps {

                echo "=========================================="
                echo "SonarQube Code Quality Gate"
                echo "=========================================="

                timeout(time: 5, unit: 'MINUTES') {

                    waitForQualityGate(
                        abortPipeline: true
                    )
                }

                echo ""
                echo "=========================================="
                echo "Code Quality Gate PASSED"
                echo "=========================================="
            }
        }


        // =========================================================
        // 5. DEPENDENCY SCAN
        // =========================================================

        stage('5. Dependency Scan') {

            steps {

                echo "=========================================="
                echo "Python Dependency Vulnerability Scan"
                echo "=========================================="

                sh '''
                    set -e

                    echo "Installing pip-audit..."

                    python3 -m pip install --user --upgrade pip-audit

                    echo ""
                    echo "pip-audit Version:"

                    python3 -m pip_audit --version

                    echo ""
                    echo "Starting Dependency Scan..."

                    rm -f pip-audit-report.json

                    for i in 1 2 3
                    do

                        echo ""
                        echo "pip-audit attempt: $i"

                        if python3 -m pip_audit \
                            -r requirements.txt \
                            -f json \
                            -o pip-audit-report.json
                        then

                            echo "Dependency scan completed successfully."
                            break

                        else

                            if [ "$i" -eq 3 ]; then

                                echo "ERROR: Dependency scan failed after 3 attempts."
                                exit 1

                            fi

                            echo "Dependency scan failed."
                            echo "Retrying in 10 seconds..."

                            sleep 10

                        fi

                    done

                    if [ ! -f pip-audit-report.json ]; then

                        echo "ERROR: Dependency scan report was not generated."
                        exit 1

                    fi

                    echo ""
                    echo "Dependency vulnerability scan completed."
                '''

                archiveArtifacts(
                    artifacts: 'pip-audit-report.json',
                    allowEmptyArchive: false
                )
            }
        }


        // =========================================================
        // 6. TRIVY FILE SCAN
        // =========================================================

        stage('6. Trivy File Scan') {

            steps {

                echo "=========================================="
                echo "Trivy Filesystem Security Scan"
                echo "=========================================="

                sh '''
                    set -e

                    if ! command -v trivy >/dev/null 2>&1; then

                        echo "ERROR: Trivy is not installed."
                        exit 1

                    fi

                    echo "Trivy Version:"
                    trivy --version

                    echo ""
                    echo "=========================================="
                    echo "Trivy Vulnerability / Secret / Misconfiguration Scan"
                    echo "=========================================="

                    trivy fs \
                        --scanners vuln,secret,misconfig \
                        --severity HIGH,CRITICAL \
                        --format table \
                        .

                    echo ""
                    echo "Generating Trivy JSON Report..."

                    rm -f trivy-report.json

                    trivy fs \
                        --scanners vuln,secret,misconfig \
                        --severity HIGH,CRITICAL \
                        --format json \
                        --output trivy-report.json \
                        .

                    if [ ! -f trivy-report.json ]; then

                        echo "ERROR: Trivy report was not generated."
                        exit 1

                    fi

                    echo ""
                    echo "Trivy filesystem scan completed."
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

            echo "1. Clean Workspace       : PASSED"
            echo "2. Git Checkout          : PASSED"
            echo "3. SonarQube Analysis    : PASSED"
            echo "4. Code Quality Gate     : PASSED"
            echo "5. Dependency Scan       : PASSED"
            echo "6. Trivy File Scan       : PASSED"

            echo "=========================================="
        }


        failure {

            echo "=========================================="
            echo "TEST CODE PIPELINE FAILED"
            echo "=========================================="

            echo "Please check the Jenkins console output."

            echo ""
            echo "Pipeline Stages:"

            echo "1. Clean Workspace"
            echo "2. Git Checkout"
            echo "3. SonarQube Analysis"
            echo "4. Code Quality Gate"
            echo "5. Dependency Scan"
            echo "6. Trivy File Scan"

            echo "=========================================="
        }
    }
}
