pipeline {
agent any
stages {
	stage('Build') {
	parallel {
		stage('Build') {
		steps {
			sh 'echo "building the repo"'
		}
		}
	}
	}

	stage('Test') {
	steps {
		sh 'echo "TESTTTTT"'
		sh 'virtualenv venv && . venv/bin/activate && pip install -r requirements.txt'
		sh 'python3 main.py'
		input(id: "Deploy Gate", message: "Deploy ${params.project_name}?", ok: 'Deploy')
	}
	}

	stage('Deploy')
	{
	steps {
		echo "deploying the application"
		sh 'virtualenv venv && . venv/bin/activate && pip install -r requirements.txt'
		sh "sudo nohup python3 main.py> log.txt 2>&1 &"
		
	}
	}
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

