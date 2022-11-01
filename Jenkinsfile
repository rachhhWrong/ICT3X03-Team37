#!/bin/bash
pipeline {
agent any

environment {
    COMPOSE_FILE = 'containers/docker-compose.debug.yml'
    DOCKER_FILE = 'containers/web/Dockerfile'

  }
stages {
    stage('Test') {
	    steps {
	        echo 'Hello from Dev branch'
            sh 'echo "Testing Phase"'
            sh 'echo "Building the Repo"'
		    sh 'echo "Installing Requirements.txt"'
		    sh 'pip install -r requirements.txt'
		    echo "Requirements met"
		    //sh 'python3 test.py'
             echo "Getting Docker Information"
		    sh 'docker info'
		    sh 'docker version'
		    sh 'docker compose version'

		    echo 'test completed'

		    
	    }
	}

    stage('Build') {
    parallel {
		stage('Build') {
		steps {
		echo 'test'
		sh 'docker compose -f ${COMPOSE_FILE} build'


		    //sh 'docker-compose -f docker-compose.debug.yaml up --build'
		    //input(id: "Deploy Gate", message: "Deploy ${params.project_name}?", ok: 'Deploy')
		}
		}
	}
	}



	stage('Deploy') {
	steps {
		echo "deploying the application"
		//sh 'FLASK_APP=main.py flask run'

	}
	post {
		always {
			echo 'The pipeline completed'
			junit allowEmptyResults: true, testResults:'**/test_reports/*.xml'
		}
		success {
			echo "Flask Application Up and running!!"
		}
		failure {
			echo 'Build stage failed'
			error('Stopping early…')
		}
	}
	


    
}
}
}
