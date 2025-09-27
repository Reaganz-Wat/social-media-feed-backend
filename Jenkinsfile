pipeline {
    agent any
    
    environment {
        NEW_VERSION = '1.3.0'
        NEW_VENV = 'venv'
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
            }
        }

        stage('Test') {
            steps {
                echo "Testing version ${NEW_VERSION}"
            }
        }

        stage('Package') {
            steps {
                echo "Packaging version ${NEW_VERSION}"
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploying version ${NEW_VERSION}"
            }
        }
    }
}