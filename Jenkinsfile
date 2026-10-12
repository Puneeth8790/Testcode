pipeline {
    agent any

    triggers {
        githubPush()
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 60, unit: 'MINUTES')
    }

    environment {
        REPO_URL = 'https://github.com/Puneeth8790/Testcode.git'
        TARGET_BRANCH = 'feature'

        // These IDs must match Jenkins configuration.
        SCANNER_HOME = tool 'sonar-scanner'
        SONAR_SERVER = 'sonar-server'
        SONAR_TOKEN_CREDENTIAL = 'sonar-test'
        SONAR_PROJECT_NAME = 'Test Code'
        SONAR_PROJECT_KEY = 'Test-Code'

        DOCKER_IMAGE = 'testdemo'
        DOCKER_TAG = 'v1'
        DOCKER_CREDENTIALS = 'dockerhub-credentials'
        CONTAINER_NAME = 'TestDemo'
        HOST_PORT = '8000'
        CONTAINER_PORT = '8000'

        PROMETHEUS_URL = 'http://localhost:9090'
        APP_HEALTH_URL = 'http://localhost:8000/'
    }

    stages {
        stage('1. Clean Workspace') {
            steps {
                echo 'Cleaning Jenkins workspace...'
                deleteDir()
            }
        }

        stage('2. Git Checkout') {
            steps {
                git branch: "${TARGET_BRANCH}", url: "${REPO_URL}"
                sh '''
                    set -eu
                    echo "Current branch:"
                    git branch --show-current
                    echo "Latest commit:"
                    git log -1 --oneline
                '''
            }
        }

        // Generate coverage before SonarQube analysis.
        stage('3. Unit Tests and Code Coverage') {
            steps {
                sh '''
                    set -eu
                    python3 --version
                    python3 -m pip --version
                    test -f requirements.txt
                    test -d tests
                    test -d app

                    python3 -m pip install --user -r requirements.txt
                    python3 -m pip install --user pytest pytest-cov

                    python3 -m pytest tests/ \\
                        --cov=app \\
                        --cov-report=term-missing \\
                        --cov-report=xml:coverage.xml \\
                        --cov-report=html:htmlcov

                    test -s coverage.xml
                    echo "Coverage report generated successfully."
                '''
                archiveArtifacts(
                    artifacts: 'coverage.xml,htmlcov/**',
                    allowEmptyArchive: false
                )
            }
        }

        stage('4. SonarQube Analysis') {
            steps {
                withSonarQubeEnv("${SONAR_SERVER}") {
                    withCredentials([
                        string(
                            credentialsId: "${SONAR_TOKEN_CREDENTIAL}",
                            variable: 'SONAR_AUTH_TOKEN'
                        )
                    ]) {
                        sh '''
                            set -eu
                            test -s coverage.xml

                            echo "SonarQube URL: $SONAR_HOST_URL"
                            "$SCANNER_HOME/bin/sonar-scanner" \\
                                -Dsonar.projectName="$SONAR_PROJECT_NAME" \\
                                -Dsonar.projectKey="$SONAR_PROJECT_KEY" \\
                                -Dsonar.sources=app \\
                                -Dsonar.tests=tests \\
                                -Dsonar.python.coverage.reportPaths=coverage.xml \\
                                -Dsonar.host.url="$SONAR_HOST_URL" \\
                                -Dsonar.token="$SONAR_AUTH_TOKEN"
                        '''
                    }
                }
            }
        }

        stage('5. SonarQube Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
                echo 'SonarQube Quality Gate passed.'
            }
        }

        stage('6. Dependency Scan') {
            steps {
                sh '''
                    set -eu
                    python3 -m pip install --user --upgrade pip-audit
                    rm -f pip-audit-report.json

                    attempt=1
                    while [ "$attempt" -le 3 ]; do
                        if python3 -m pip_audit \\
                            -r requirements.txt \\
                            -f json \\
                            -o pip-audit-report.json; then
                            echo "Dependency scan completed."
                            break
                        fi

                        if [ "$attempt" -eq 3 ]; then
                            echo "ERROR: Dependency scan failed after 3 attempts."
                            exit 1
                        fi

                        attempt=$((attempt + 1))
                        echo "Dependency scan failed; retrying in 10 seconds..."
                        sleep 10
                    done

                    test -s pip-audit-report.json
                '''
            }
            post {
                always {
                    archiveArtifacts(
                        artifacts: 'pip-audit-report.json',
                        allowEmptyArchive: true
                    )
                }
            }
        }

        stage('7. Docker Build') {
            steps {
                sh '''
                    set -eu
                    docker --version
                    test -f Dockerfile
                    docker build -t "${DOCKER_IMAGE}:${DOCKER_TAG}" .
                    docker image inspect "${DOCKER_IMAGE}:${DOCKER_TAG}" >/dev/null
                '''
            }
        }

        stage('8. Docker Hub Login') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: "${DOCKER_CREDENTIALS}",
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    sh '''
                        set -eu
                        echo "$DOCKER_PASSWORD" | docker login \\
                            --username "$DOCKER_USERNAME" \\
                            --password-stdin
                    '''
                }
            }
        }

        stage('9. Docker Push') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: "${DOCKER_CREDENTIALS}",
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    sh '''
                        set -eu
                        REMOTE_IMAGE="$DOCKER_USERNAME/$DOCKER_IMAGE:$DOCKER_TAG"
                        docker tag "$DOCKER_IMAGE:$DOCKER_TAG" "$REMOTE_IMAGE"
                        docker push "$REMOTE_IMAGE"
                    '''
                }
            }
        }

        stage('10. Docker Pull') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: "${DOCKER_CREDENTIALS}",
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    sh '''
                        set -eu
                        REMOTE_IMAGE="$DOCKER_USERNAME/$DOCKER_IMAGE:$DOCKER_TAG"
                        docker pull "$REMOTE_IMAGE"
                    '''
                }
            }
        }

         stage('11. Trivy Docker Image Scan') {

            steps {

                echo "=========================================="
                echo "Trivy Docker Image Security Scan"
                echo "=========================================="

                withCredentials([
                    usernamePassword(
                        credentialsId: "${DOCKER_CREDENTIALS}",
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {

                    sh '''
                        set -e

                        echo "Trivy Version:"
                        trivy --version

                        echo ""
                        echo "=========================================="
                        echo "Scanning Docker Image"
                        echo "=========================================="

                        trivy image \
                            --severity HIGH,CRITICAL \
                            --format table \
                            "$DOCKER_USERNAME/${DOCKER_IMAGE}:${DOCKER_TAG}"

                        echo ""
                        echo "=========================================="
                        echo "Generating Trivy JSON Report"
                        echo "=========================================="

                        rm -f trivy-image-report.json

                        trivy image \
                            --severity HIGH,CRITICAL \
                            --format json \
                            --output trivy-image-report.json \
                            "$DOCKER_USERNAME/${DOCKER_IMAGE}:${DOCKER_TAG}"

                        if [ ! -f trivy-image-report.json ]; then

                            echo "ERROR: Trivy image report was not generated."
                            exit 1

                        fi

                        echo ""
                        echo "Trivy Docker Image Scan Completed."
                    '''

                    archiveArtifacts(
                        artifacts: 'trivy-image-report.json',
                        allowEmptyArchive: false
                    )
                }
            }
        }



        stage('12. Docker Run / Deploy') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: "${DOCKER_CREDENTIALS}",
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    sh '''
                        set -eu
                        REMOTE_IMAGE="$DOCKER_USERNAME/$DOCKER_IMAGE:$DOCKER_TAG"

                        docker stop "$CONTAINER_NAME" || true
                        docker rm "$CONTAINER_NAME" || true

                        docker run -d \\
                            --restart unless-stopped \\
                            --name "$CONTAINER_NAME" \\
                            -p "$HOST_PORT:$CONTAINER_PORT" \\
                            "$REMOTE_IMAGE"

                        docker ps --filter "name=^/${CONTAINER_NAME}$"
                    '''
                }
            }
        }

        stage('13. Prometheus Metrics Monitoring') {
            steps {
                sh '''
                    set -eu
                    echo "Checking Prometheus at $PROMETHEUS_URL"
                    curl -fsS --max-time 10 "$PROMETHEUS_URL/-/healthy"
                    curl -fsS --max-time 10 "$PROMETHEUS_URL/-/ready"
                    curl -fsS --max-time 10 --get \\
                        --data-urlencode 'query=up' \\
                        "$PROMETHEUS_URL/api/v1/query"
                    echo "Prometheus checks passed."
                '''
            }
        }

        stage('14. Deployment Verification') {
            steps {
                sh '''
                    set -eu
                    if ! docker ps --format '{{.Names}}' | grep -Fxq "$CONTAINER_NAME"; then
                        echo "ERROR: Container $CONTAINER_NAME is not running."
                        docker logs "$CONTAINER_NAME" || true
                        exit 1
                    fi

                    echo "Checking application endpoint: $APP_HEALTH_URL"
                    curl -fsS --max-time 15 "$APP_HEALTH_URL" >/dev/null
                    echo "Deployment verification passed."
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully.'
        }
        failure {
            echo 'CI/CD pipeline failed. Review the failed stage logs.'
        }
        always {
            sh 'docker logout >/dev/null 2>&1 || true'
        }
    }
}
