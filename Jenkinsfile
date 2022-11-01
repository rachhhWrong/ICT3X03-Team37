pipeline {
agent any
tools {
	// docker credentials
	'org.jenkinsci.plugins.docker.commons.tools.DockerTool' 'default'
}
stages {
	stage('Build') {
		git branch: 'Database', changelog: false, credentialsId: 'demogithubkey', poll: false, url: 'git@github.com:rachhhWrong/ICT3X03-Team37.git'

		dir('containers') {
			sh "docker compose build --pull"
		}
	}
	stage('Test'){
		steps{
			script{
				docker.image("3x03/db").withRun("--env-file containers/dev.env"){_->
					docker.image("3x03/web").withRun("--env-file containers/dev.env","sleep infinity"){c->
						sh "docker cp test.py ${c.id}:/app/test.py"
						sh "docker exec -t ${c.id} python test.py"
					}
				}
			}
		}
	}
    // stage('Test') {
	//     steps {
	//         echo 'Hello from Dev branch'
    //         sh 'echo "Testing Phase"'
    //         sh 'echo "Building the Repo"'
	// 	    sh 'echo "Installing Requirements.txt"'
	// 	    sh 'pip install -r requirements.txt'
	// 	    sh 'echo "Requirements met"'
	// 	    sh 'python3 test.py'
	// 	    echo 'test completed'
		    
	//     }
	// }

    // stage('Build') {
    // parallel {
	// 	stage('Build') {
	// 	steps {
	// 	    sh 'python3 test.py'
	// 	    //input(id: "Deploy Gate", message: "Deploy ${params.project_name}?", ok: 'Deploy')
	// 	}
	// 	}
	// }
	// }
	stage('Deploy') {
	steps {
		echo "deploying the application"
		// sh 'FLASK_APP=main.py flask run'
		withCredentials([usernamePassword(credentialsId: 'd72d3cc9-af19-4e0e-a8a3-9b83d2526e3e', passwordVariable: 'MONGO_INITDB_ROOT_PASSWORD', usernameVariable: 'MONGO_INITDB_ROOT_USERNAME')]) {
			withCredentials([usernamePassword(credentialsId: '5d318559-a4f3-4586-acd5-504d409403e5', passwordVariable: 'MONGO_NONROOT_PASSWORD', usernameVariable: 'MONGO_NONROOT_USERNAME')]) {
				dir('containers') {
					sh "docker compose up -d"
				}
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
}
}
