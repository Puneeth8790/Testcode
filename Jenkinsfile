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

        SCANNER_HOME = tool 'sonar-scanner'

        SONAR_SERVER = "sonar-server"
        SONAR_TOKEN_CREDENTIAL = "sonar-test"

        SONAR_PROJECT_NAME = "Test Code"
        SONAR_PROJECT_KEY = "Test-Code"
    }

    stages {

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

        stage('2. Unit Test & Code Coverage') {
            steps {
                sh '''
                    set -e

                    echo "Python version:"
                    python3 --version

                    echo "Installing dependencies..."

                    python3 -m pip install --user -r requirements.txt

                    echo "Checking FastAPI..."
                    python3 -c "import fastapi; print('FastAPI installed successfully')"

                    echo "Running unit tests..."

                    python3 -m pytest \
                        tests/ \
                        --cov=app \
                        --cov-report=term-missing \
                        --cov-report=xml:coverage.xml \
                        --cov-report=html:htmlcov

                    echo "Checking coverage.xml..."

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

        stage('3. SonarQube Analysis - Test Code') {
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
                            echo "Project: Test Code"
                            echo "Key: Test-Code"
                            echo "Branch: feature"
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
                                -Dsonar.branch.name="$TARGET_BRANCH" \
                                -Dsonar.python.coverage.reportPaths=coverage.xml

                            echo "=========================================="
                            echo "SonarQube scan completed successfully"
                            echo "=========================================="
                        '''
                    }
                }
            }
        }

        stage('4. SonarQube Quality Gate') {
            steps {

                timeout(time: 5, unit: 'MINUTES') {

                    waitForQualityGate(
                        abortPipeline: true
                    )
                }
            }
        }
    }

    post {

        success {
            echo "=========================================="
            echo "Test Code Pipeline SUCCESS"
            echo "=========================================="
        }

        failure {
            echo "=========================================="
            echo "Test Code Pipeline FAILED"
            echo "Check Jenkins console output"
            echo "=========================================="
        }
    }
}
