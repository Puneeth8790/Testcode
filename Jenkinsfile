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

        // Jenkins Credentials
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

                echo ""
                echo "=========================================="
                echo "Repository Structure"
                echo "=========================================="

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

                    echo "=========================================="
                    echo "Python Version"
                    echo "=========================================="

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


                    echo ""
                    echo "=========================================="
                    echo "Installing Application Dependencies"
                    echo "=========================================="

                    python3 -m pip install --user -r requirements.txt


                    echo ""
                    echo "=========================================="
                    echo "Installing Test Dependencies"
                    echo "=========================================="

                    python3 -m pip install --user pytest pytest-cov


                    echo ""
                    echo "=========================================="
                    echo "Installed FastAPI Check"
                    echo "=========================================="

                    python3 -c "import fastapi; print('FastAPI version:', fastapi.__version__)"


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


                    echo ""
                    echo "Test files found:"
                    echo "$TEST_FILES"


                    echo ""
                    echo "=========================================="
                    echo "Running Unit Tests"
                    echo "=========================================="

                    python3 -m pytest \
                        tests/ \
                        --cov=app \
                        --cov-report=term-missing \
                        --cov-report=xml:coverage.xml \
                        --cov-report=html:htmlcov


                    echo ""
                    echo "=========================================="
                    echo "UNIT TESTS COMPLETED"
                    echo "=========================================="


                    echo ""
                    echo "=========================================="
                    echo "Checking Coverage XML"
                    echo "=========================================="

                    if [ ! -f coverage.xml ]; then

                        echo "ERROR: coverage.xml was not generated."
                        exit 1

                    fi

                    ls -lh coverage.xml


                    echo ""
                    echo "=========================================="
                    echo "Checking HTML Coverage"
                    echo "=========================================="

                    if [ ! -d htmlcov ]; then

                        echo "ERROR: htmlcov directory was not generated."
                        exit 1

                    fi

                    ls -ld htmlcov


                    echo ""
                    echo "=========================================="
                    echo "CODE COVERAGE COMPLETED"
                    echo "=========================================="
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
                            echo "Checking Coverage Report"
                            echo "=========================================="

                            if [ ! -f coverage.xml ]; then

                                echo "ERROR: coverage.xml not found."
                                exit 1

                            fi

                            ls -lh coverage.xml


                            echo ""
                            echo "=========================================="
                            echo "Starting SonarQube Scanner"
                            echo "=========================================="

                            "$SCANNER_HOME/bin/sonar-scanner" \
                                -Dsonar.projectName="$SONAR_PROJECT_NAME" \
                                -Dsonar.projectKey="$SONAR_PROJECT_KEY" \
                                -Dsonar.sources=app \
                                -Dsonar.tests=tests \
                                -Dsonar.host.url="$SONAR_HOST_URL" \
                                -Dsonar.token="$SONAR_AUTH_TOKEN" \
                                -Dsonar.branch.name="$TARGET_BRANCH" \
                                -Dsonar.python.coverage.reportPaths=coverage.xml


                            echo ""
                            echo "=========================================="
                            echo "SONARQUBE ANALYSIS COMPLETED"
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
                echo "Waiting for SonarQube Quality Gate"
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

            Unit Tests      : PASSED
            Code Coverage   : GENERATED
            SonarQube Scan  : PASSED
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
