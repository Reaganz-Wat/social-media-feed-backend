pipeline {
    agent any
    environment {
        NEW_VERSION = '1.3.0'
        NEW_VENV = 'venv'
        DOCKER_IMAGE = 'social-media-backend'
        POSTGRES_DB = 'test_social_media_db'
        POSTGRES_USER = 'postgres'
        POSTGRES_PASSWORD = 'password'
        REDIS_URL = 'redis://localhost:6379/0'
    }
    stages {
        stage('Setup Python') {
            steps {
                script {
                    sh """
                        python3 -m venv ${NEW_VENV}
                        . ${NEW_VENV}/bin/activate
                        pip3 install -r requirements.txt
                        python3 manage.py test --verbosity=2
                    """
                }
            }
        }
        stage('Build') {
            steps {
                echo "Building version ${NEW_VERSION}"
                sh """
                    . ${NEW_VENV}/bin/activate
                    
                    # Setup test database
                    docker run -d --name test_postgres -e POSTGRES_DB=${POSTGRES_DB} -e POSTGRES_USER=${POSTGRES_USER} -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} -p 5433:5432 postgres:13
                    docker run -d --name test_redis -p 6380:6379 redis:6
                    sleep 10
                    
                    # Run migrations
                    export DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5433/${POSTGRES_DB}
                    python3 manage.py migrate
                    
                    # Build Docker image
                    docker build -t ${DOCKER_IMAGE}:${NEW_VERSION} .
                """
            }
        }
        stage('Test') {
            steps {
                echo "Testing version ${NEW_VERSION}"
                sh """
                    . ${NEW_VENV}/bin/activate
                    export DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5433/${POSTGRES_DB}
                    export REDIS_URL=${REDIS_URL}
                    
                    # Run all tests
                    python3 manage.py test --verbosity=2
                    
                    # Test GraphQL endpoints
                    python3 manage.py shell -c "
                    from django.test import Client
                    client = Client()
                    response = client.post('/graphql', {'query': '{__schema{types{name}}}'})
                    print('GraphQL endpoint test:', response.status_code)
                    "
                """
            }
        }
        stage('Package') {
            steps {
                echo "Packaging version ${NEW_VERSION}"
                sh """
                    # Tag Docker image for deployment
                    docker tag ${DOCKER_IMAGE}:${NEW_VERSION} ${DOCKER_IMAGE}:latest
                    
                    # Create deployment package
                    mkdir -p package
                    cp docker-compose.yml package/
                    cp requirements.txt package/
                    echo "${NEW_VERSION}" > package/VERSION
                """
                
                archiveArtifacts artifacts: 'package/**', fingerprint: true
            }
        }
        stage('Deploy') {
            steps {
                echo "Deploying version ${NEW_VERSION}"
                sh """
                    # Stop old containers
                    docker stop social-media-app || true
                    docker rm social-media-app || true
                    
                    # Deploy new version
                    docker run -d --name social-media-app -p 8000:8000 \
                        -e POSTGRES_DB=${POSTGRES_DB} \
                        -e POSTGRES_USER=${POSTGRES_USER} \
                        -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
                        -e REDIS_URL=${REDIS_URL} \
                        ${DOCKER_IMAGE}:${NEW_VERSION}
                    
                    # Wait for service to start
                    sleep 30
                    
                    # Health check
                    curl -f http://localhost:8000/admin/ || echo "Service not ready yet"
                """
            }
        }
    }
    post {
        always {
            sh """
                # Cleanup test containers
                docker stop test_postgres test_redis || true
                docker rm test_postgres test_redis || true
                rm -rf ${NEW_VENV}
            """
        }
        success {
            echo "Pipeline completed successfully for version ${NEW_VERSION}"
        }
        failure {
            echo "Pipeline failed for version ${NEW_VERSION}"
        }
    }
}
