pipeline {
agent any
tools {
	// docker credentials
	'org.jenkinsci.plugins.docker.commons.tools.DockerTool' 'default'
}
stages {

    stage('Check Requirements & Dump Docker info') {
	    steps {
	        echo 'Hello from Dev branch'
            sh 'echo "Testing Phase"'
            sh 'echo "Building the Repo"'
		    sh 'echo "Installing Requirements.txt"'
		    sh 'pip install -r requirements.txt'
		    echo "Requirements met"

            echo "Getting Docker Information"
		    sh 'docker info'
		    sh 'docker version'
		    sh 'docker compose version'


	    }
	}

	stage('Build Docker Compose') {
		steps {
			//git branch: 'Database', changelog: false, credentialsId: 'demogithubkey', poll: false, url: 'git@github.com:rachhhWrong/ICT3X03-Team37.git'

			dir('containers') {
				sh "docker compose build --pull"
			}
		}
	}
	stage('DependencyCheck') {
		steps {
			script {
				docker.image("3x03/web").withRun("","sleep infinity"){c->
					sh "docker exec -t ${c.id} pip freeze > requirements.txt"
				}
			}
			dependencyCheck additionalArguments: '--format HTML --format XML', odcInstallation: 'Default'
		}
		post {
			success {
				dependencyCheckPublisher pattern: 'dependency-check-report.xml'
			}
		}
	}

	stage('Docker Test') {
		steps{
			script{
				docker.image("3x03/db").withRun("--env-file containers/dev.env"){_->
					docker.image("3x03/web").withRun("--env-file containers/dev.env -e MAIL_USERNAME=fake@gmail.com -e MAIL_PASSWORD=fakepassword -e STRIPE_SECRET_KEY=fakekey",){c->
						sh "docker cp test.py ${c.id}:/app/test.py"
						sh "docker exec -t ${c.id} python test.py"
					}
				}
			}
		}
	}

	stage('Deploy') {
	steps {
		echo "Deploying the Application"
		withCredentials([
			usernamePassword(credentialsId: 'd72d3cc9-af19-4e0e-a8a3-9b83d2526e3e', passwordVariable: 'MONGO_INITDB_ROOT_PASSWORD', usernameVariable: 'MONGO_INITDB_ROOT_USERNAME'),
			usernamePassword(credentialsId: '5d318559-a4f3-4586-acd5-504d409403e5', passwordVariable: 'MONGO_NONROOT_PASSWORD', usernameVariable: 'MONGO_NONROOT_USERNAME'),
			string(credentialsId: 'FLASK_SECRET_KEY', variable: 'SECRET_KEY'),
			usernamePassword(credentialsId: '487d30df-f5c6-4798-ad51-af69d39e7c1a', passwordVariable: 'MAIL_PASSWORD', usernameVariable: 'MAIL_USERNAME'),
			string(credentialsId: '2261ab67-559f-4399-8e23-ca5064016306', variable: 'STRIPE_SECRET_KEY')
			]) {
				dir('containers') {
					sh "docker compose up -d"
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

			sleep 10
			echo "Checking if containers are still running"
			script {
				RUN_STATUS = sh (
					script: "docker inspect --format='{{.State.Running}}' 3x03-team37-web-1",
					returnStdout: true
				).trim()
				if (RUN_STATUS == "false") {
					sh "docker logs --tail 50 3x03-team37-web-1"
					error('Docker container error was detected')
				}
			}

			echo "Shutting down compose to save resources"
			dir('containers') {
				//sh "docker compose down"
			}
		}
		failure {
			echo 'Build stage failed'
			error('Stopping early…')
		}
	}




}
}
}
