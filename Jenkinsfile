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

        // =========================================================
        // DOCKER
        // =========================================================

        DOCKER_IMAGE = "testdemo"
        DOCKER_TAG = "v1"

        // Jenkins credential ID
        DOCKER_CREDENTIALS = "dockerhub-credentials"

        // Docker Hub repository
        // Example: Puneeth8790/testdemo:v1
        DOCKER_HUB_IMAGE = "Puneeth8790/testdemo:v1"

        // Container
        CONTAINER_NAME = "TestDemo"
        HOST_PORT = "8000"
        CONTAINER_PORT = "8000"
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
        // 6. DOCKER BUILD
        // =========================================================

        stage('6. Docker Build') {

            steps {

                echo "=========================================="
                echo "Docker Image Build"
                echo "=========================================="

                sh '''
                    set -e

                    echo "Docker Version:"
                    docker --version

                    echo ""
                    echo "Building Docker Image..."

                    docker build \
                        -t "${DOCKER_IMAGE}:${DOCKER_TAG}" \
                        .

                    echo ""
                    echo "Docker Image Build Completed."

                    echo ""
                    echo "Docker Image:"
                    docker images | grep "${DOCKER_IMAGE}" || true
                '''
            }
        }


        // =========================================================
        // 7. DOCKER HUB LOGIN
        // =========================================================

        stage('7. Docker Hub Login') {

            steps {

                echo "=========================================="
                echo "Docker Hub Login"
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

                        echo "Logging in to Docker Hub..."

                        echo "$DOCKER_PASSWORD" | docker login \
                            -u "$DOCKER_USERNAME" \
                            --password-stdin

                        echo "Docker Hub Login Successful."
                    '''
                }
            }
        }


        // =========================================================
        // 8. DOCKER TAG & PUSH
        // =========================================================

        stage('8. Docker Push') {

            steps {

                echo "=========================================="
                echo "Docker Image Tag & Push"
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

                        echo "Docker Hub Username:"
                        echo "$DOCKER_USERNAME"

                        echo ""
                        echo "Tagging Docker Image..."

                        docker tag \
                            "${DOCKER_IMAGE}:${DOCKER_TAG}" \
                            "$DOCKER_USERNAME/${DOCKER_IMAGE}:${DOCKER_TAG}"

                        echo ""
                        echo "Docker Image Push..."

                        docker push \
                            "$DOCKER_USERNAME/${DOCKER_IMAGE}:${DOCKER_TAG}"

                        echo ""
                        echo "Docker Image Push Completed."
                    '''
                }
            }
        }


        // =========================================================
        // 9. DOCKER PULL
        // =========================================================

        stage('9. Docker Pull') {

            steps {

                echo "=========================================="
                echo "Docker Image Pull"
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

                        echo "Removing local Docker Hub image..."

                        docker rmi \
                            "$DOCKER_USERNAME/${DOCKER_IMAGE}:${DOCKER_TAG}" \
                            || true

                        echo ""
                        echo "Pulling Docker Image from Docker Hub..."

                        docker pull \
                            "$DOCKER_USERNAME/${DOCKER_IMAGE}:${DOCKER_TAG}"

                        echo ""
                        echo "Docker Image Pull Completed."

                        echo ""
                        echo "Pulled Image:"

                        docker images | grep "${DOCKER_IMAGE}" || true
                    '''
                }
            }
        }


        // =========================================================
        // 10. TRIVY DOCKER IMAGE SCAN
        // =========================================================

        stage('10. Trivy Docker Image Scan') {

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


        // =========================================================
        // 11. DOCKER RUN
        // =========================================================

        stage('11. Docker Run') {

            steps {

                echo "=========================================="
                echo "Docker Container Deployment"
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

                        echo "Stopping existing container..."

                        docker stop "${CONTAINER_NAME}" || true

                        echo ""
                        echo "Removing existing container..."

                        docker rm "${CONTAINER_NAME}" || true

                        echo ""
                        echo "Starting Docker Container..."

                        docker run -d \
                            --name "${CONTAINER_NAME}" \
                            -p "${HOST_PORT}:${CONTAINER_PORT}" \
                            "$DOCKER_USERNAME/${DOCKER_IMAGE}:${DOCKER_TAG}"

                        echo ""
                        echo "Docker Container Started Successfully."

                        echo ""
                        echo "Container Status:"

                        docker ps \
                            --filter "name=${CONTAINER_NAME}"

                        echo ""
                        echo "Waiting for application to start..."

                        sleep 10

                        echo ""
                        echo "Container Logs:"

                        docker logs \
                            --tail 50 \
                            "${CONTAINER_NAME}"

                        echo ""
                        echo "=========================================="
                        echo "Docker Deployment Completed"
                        echo "=========================================="
                    '''
                }
            }
        }

        stage('12. Prometheus Metrics Monitoring') {
    steps {
        echo 'Checking Prometheus monitoring'

        sh '''
            set -e

            PROMETHEUS_URL="http://localhost:9090"

            echo "Checking Prometheus health..."
            curl -fsS --max-time 10 \
                "$PROMETHEUS_URL/-/healthy"

            echo ""
            echo "Checking Prometheus readiness..."
            curl -fsS --max-time 10 \
                "$PROMETHEUS_URL/-/ready"

            echo ""
            echo "Checking Prometheus query API..."
            curl -fsS --get \
                --data-urlencode 'query=up' \
                "$PROMETHEUS_URL/api/v1/query"

            echo ""
            echo "Prometheus checks completed successfully."
        '''
    }
}

        stage('13. Deployment Verification') {

            steps {

                echo "=========================================="
                echo "Deployment Verification"
                echo "=========================================="

                sh '''
                    set -e

                    echo "Checking Docker Container..."

                    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then

                        echo "Container ${CONTAINER_NAME} is RUNNING."

                    else

                        echo "ERROR: Container ${CONTAINER_NAME} is NOT running."
                        echo ""
                        echo "Container Logs:"
                        docker logs "${CONTAINER_NAME}" || true

                        exit 1

                    fi

                    echo ""
                    echo "Checking Port ${HOST_PORT}..."

                    if command -v curl >/dev/null 2>&1; then

                        curl -f \
                            --max-time 10 \
                            "http://localhost:${HOST_PORT}" \
                            || echo "Application endpoint check returned non-success."

                    else

                        echo "curl is not installed. Skipping HTTP check."

                    fi

                    echo ""
                    echo "=========================================="
                    echo "Deployment Verification Completed"
                    echo "=========================================="
                '''
            }
        }
    }
}
