pipeline {

    agent any

    // ============================================================
    // TRIGGERS
    // ============================================================
    triggers {
        githubPush()
        pollSCM('H/2 * * * *')
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

        // ============================================================
        // GITHUB
        // ============================================================
        REPO_URL = "https://github.com/Puneeth8790/Testcode.git"
        TARGET_BRANCH = "feature"

        // ============================================================
        // SONARQUBE
        // ============================================================
        SCANNER_HOME = tool 'sonar-scanner'

        SONAR_PROJECT_NAME = "Test Code"
        SONAR_PROJECT_KEY = "Test-Code"

        // Jenkins -> Manage Jenkins -> System
        SONAR_SERVER = "sonar-server"

        // Jenkins Credential ID
        SONAR_TOKEN_CREDENTIAL = "sonar-token"
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

                echo ""
                echo "GitHub Checkout Completed Successfully"
            }
        }


        // ============================================================
        // 2. CODE COVERAGE
        // ============================================================
        stage('2. Code Coverage') {

            steps {

                echo "=========================================="
                echo "Code Coverage / Unit Tests"
                echo "=========================================="

                sh '''
                    set -e

                    echo "Current Directory:"
                    pwd

                    echo ""
                    echo "Repository Files:"
                    ls -la

                    # ------------------------------------------------
                    # Check backend directory
                    # ------------------------------------------------
                    if [ ! -d "backend" ]; then

                        echo ""
                        echo "WARNING: backend directory not found."
                        echo "Skipping Python code coverage."

                        exit 0
                    fi

                    cd backend

                    echo ""
                    echo "=========================================="
                    echo "Installing Test Dependencies"
                    echo "=========================================="

                    python3 -m pip install --user pytest pytest-cov

                    echo ""
                    echo "=========================================="
                    echo "Searching for Unit Test Files"
                    echo "=========================================="

                    TEST_FILES=$(find . -type f \\( \
                        -name "test_*.py" \
                        -o -name "*_test.py" \
                    \\) \
                    ! -path "./venv/*" \
                    ! -path "./.venv/*" \
                    ! -path "./env/*" \
                    ! -path "./.env/*" \
                    | sort || true)

                    if [ -n "$TEST_FILES" ]; then

                        echo ""
                        echo "Test files found:"
                        echo "$TEST_FILES"

                        echo ""
                        echo "=========================================="
                        echo "Running Unit Tests"
                        echo "=========================================="

                        python3 -m pytest \
                            --cov=. \
                            --cov-report=term \
                            --cov-report=xml:coverage.xml \
                            --cov-report=html:htmlcov

                        echo ""
                        echo "=========================================="
                        echo "Unit Tests Completed"
                        echo "=========================================="

                        echo ""
                        echo "=========================================="
                        echo "Coverage Report"
                        echo "=========================================="

                        if [ -f "coverage.xml" ]; then

                            echo "Coverage XML found:"
                            ls -lh coverage.xml

                            echo ""
                            echo "Coverage XML generated successfully."

                        else

                            echo ""
                            echo "ERROR: coverage.xml was not generated."

                            exit 1
                        fi

                        if [ -d "htmlcov" ]; then

                            echo ""
                            echo "HTML coverage report generated:"
                            ls -ld htmlcov

                        fi

                    else

                        echo ""
                        echo "=========================================="
                        echo "NO UNIT TEST FILES FOUND"
                        echo "=========================================="

                        echo "Expected test file names:"
                        echo "  test_*.py"
                        echo "  *_test.py"

                        echo ""
                        echo "No unit tests were found."
                        echo "Coverage will not be generated."

                    fi

                    cd ..
                '''

                archiveArtifacts(
                    artifacts: 'backend/coverage.xml,backend/htmlcov/**',
                    allowEmptyArchive: true
                )
            }
        }


        // ============================================================
        // 3. SONARQUBE ANALYSIS
        // ============================================================
        stage('3. SonarQube Analysis') {

            steps {

                echo "=========================================="
                echo "SonarQube Analysis"
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

                            echo "=========================================="
                            echo "SonarQube Configuration"
                            echo "=========================================="

                            echo "Project Name : $SONAR_PROJECT_NAME"
                            echo "Project Key  : $SONAR_PROJECT_KEY"
                            echo "Branch       : $TARGET_BRANCH"
                            echo "Sonar URL    : $SONAR_HOST_URL"

                            echo ""
                            echo "=========================================="
                            echo "Starting SonarQube Scan"
                            echo "=========================================="

                            cd backend

                            # ------------------------------------------------
                            # Check Coverage XML
                            # ------------------------------------------------
                            if [ -f "coverage.xml" ]; then

                                echo ""
                                echo "Coverage XML found."
                                echo "Importing Python coverage into SonarQube."

                                "$SCANNER_HOME/bin/sonar-scanner" \
                                    -Dsonar.projectName="$SONAR_PROJECT_NAME" \
                                    -Dsonar.projectKey="$SONAR_PROJECT_KEY" \
                                    -Dsonar.sources=. \
                                    -Dsonar.host.url="$SONAR_HOST_URL" \
                                    -Dsonar.token="$SONAR_AUTH_TOKEN" \
                                    -Dsonar.branch.name="$TARGET_BRANCH" \
                                    -Dsonar.python.coverage.reportPaths=coverage.xml

                            else

                                echo ""
                                echo "WARNING: coverage.xml not found."
                                echo "Running SonarQube without coverage."

                                "$SCANNER_HOME/bin/sonar-scanner" \
                                    -Dsonar.projectName="$SONAR_PROJECT_NAME" \
                                    -Dsonar.projectKey="$SONAR_PROJECT_KEY" \
                                    -Dsonar.sources=. \
                                    -Dsonar.host.url="$SONAR_HOST_URL" \
                                    -Dsonar.token="$SONAR_AUTH_TOKEN" \
                                    -Dsonar.branch.name="$TARGET_BRANCH"

                            fi

                            cd ..

                            echo ""
                            echo "=========================================="
                            echo "SonarQube Analysis Completed"
                            echo "=========================================="
                        '''
                    }
                }
            }
        }


        // ============================================================
        // 4. SONARQUBE QUALITY GATE
        // ============================================================
        stage('4. SonarQube Quality Gate') {

            steps {

                echo "=========================================="
                echo "SonarQube Quality Gate"
                echo "=========================================="

                timeout(time: 5, unit: 'MINUTES') {

                    waitForQualityGate abortPipeline: true
                }

                echo ""
                echo "=========================================="
                echo "SONARQUBE QUALITY GATE PASSED"
                echo "=========================================="
            }
        }
    }


    // ============================================================
    // POST ACTIONS
    // ============================================================
    post {

        // ============================================================
        // SUCCESS
        // ============================================================
        success {

            echo """
            ==========================================
                 JENKINS PIPELINE SUCCESS
            ==========================================

            Repository      : ${REPO_URL}
            Branch          : ${TARGET_BRANCH}

            SonarQube Project:
            ${SONAR_PROJECT_NAME}

            SonarQube Key:
            ${SONAR_PROJECT_KEY}

            Code Coverage   : COMPLETED / NO TESTS FOUND
            SonarQube Scan   : PASSED
            Quality Gate    : PASSED

            ==========================================
            """
        }


        // ============================================================
        // FAILURE
        // ============================================================
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
    }
}
