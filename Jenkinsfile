pipeline {
agent any
stages {
	stage('Build') {
	parallel {
		stage('Build') {
		steps {
			sh 'echo "Building the Repo"'
			sh 'echo "Installing Requirements.txt"'
			sh 'pip install -r requirements.txt'
		}
		}
	}
	}

	stage('Test') {
	steps {
	    if (env.BRANCH_NAME == 'Fee') {
            echo 'Hello from Fee branch'
            sh 'echo "Testing Phase"'
		    sh 'python3 main.py'
		input(id: "Deploy Gate", message: "Deploy ${params.project_name}?", ok: 'Deploy')
        } else {
            sh "echo 'Hello from ${env.BRANCH_NAME} branch!'"
        }




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

