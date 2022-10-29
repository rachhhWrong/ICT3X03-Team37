pipeline {
agent any
stages {
    stage('Test') {
	    steps {
	        echo 'Hello from Dev branch'
            sh 'echo "Testing Phase"'
            sh 'echo "Building the Repo"'
		    sh 'echo "Installing Requirements.txt"'
		    sh 'pip install -r requirements.txt'
		    sh 'echo "Requirements met"'
		    sh 'python3 test.py'
		    echo 'test completed'
		    post {
                always {junit 'test-reports/*.xml'}
            }
	    }
	}
   
    stage('Build') {
    parallel {
		stage('Build') {
		steps {
		    sh 'python3 main.py'
		    input(id: "Deploy Gate", message: "Deploy ${params.project_name}?", ok: 'Deploy')

		}
		}
	}
	}
	stage('Deploy') {
	steps {
		echo "deploying the application"
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
