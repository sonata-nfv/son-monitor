pipeline {
  agent any
  stages {
    stage('Container Build') {
      parallel {
        stage('Container Build') {
          steps {
            echo 'Building..'
          }
        }
        stage('son-monitor-manager') {
          steps {
            sh 'docker build -t registry.sonata-nfv.eu:5000/son-monitor-manager:v4.0 -f manager/Dockerfile manager/'
          }
        }
        stage('son-monitor-prometheus') {
          steps {
            sh 'docker build -t registry.sonata-nfv.eu:5000/son-monitor-prometheus:v4.0 -f prometheus/Dockerfile prometheus/'
          }
        }
        stage('son-monitor-pushgateway') {
          steps {
            sh 'docker build -t registry.sonata-nfv.eu:5000/son-monitor-pushgateway:v4.0 -f pushgateway/Dockerfile pushgateway/'
          }
        }
        stage('son-monitor-influxdb') {
          steps {
            sh 'docker build -t registry.sonata-nfv.eu:5000/son-monitor-influxdb:v4.0 -f influxDB/Dockerfile influxDB/'
          }
        }
        stage('son-monitor-snmpmng') {
          steps {
            sh 'docker build -t registry.sonata-nfv.eu:5000/son-monitor-snmpmng:v4.0 -f snmpmng/Dockerfile snmpmng/'
          }
        }
      }
    }
    stage('Tests: Preparation') {
      steps {
        echo 'Prepear for Tests'
        sh './test/unittests_preparation.sh'
      }
    }
    stage('Tests: Execution') {
      steps {
        echo 'Excute Unit Tests'
        sh './test/unittests_run_tests.sh'

        echo 'Excute Component Integration Tests'
        sh './test/inttests_run_tests.sh'
      }
    }
    stage('Tests: Clean') {
      steps {
        echo 'Remove test containers'
        sh './test/unittests_clean.sh'
      }
    }
    stage('Code Style check') {
      steps {
        echo 'Code Style check....'
      }
    }
    stage('Containers Publication') {
      parallel {
        stage('Containers Publication') {
          steps {
            echo 'Publication of containers in local registry....'
          }
        }
        stage('son-monitor-manager') {
          steps {
            sh 'docker push registry.sonata-nfv.eu:5000/son-monitor-manager:v4.0'
          }
        }
        stage('son-monitor-prometheus') {
          steps {
            sh 'docker push registry.sonata-nfv.eu:5000/son-monitor-prometheus:v4.0'
          }
        }
        stage('son-monitor-pushgateway') {
          steps {
            sh 'docker push registry.sonata-nfv.eu:5000/son-monitor-pushgateway:v4.0'
          }
        }
        stage('son-monitor-influxdb') {
          steps {
            sh 'docker push registry.sonata-nfv.eu:5000/son-monitor-influxdb:v4.0'
          }
        }
        stage('son-monitor-snmpmng') {
          steps {
            sh 'docker push registry.sonata-nfv.eu:5000/son-monitor-snmpmng:v4.0'
          }
        }
      }
    }
    stage('Deployment in sta-sp-v4.0') {
      parallel {
        stage('Deployment in sta-sp-v4.0') {
          steps {
            echo 'Deploying in sta-sp-v4.0...'
          }
        }
        stage('Deploying') {
          steps {
            sh 'rm -rf tng-devops || true'
            sh 'git clone https://github.com/sonata-nfv/tng-devops.git'
            dir(path: 'tng-devops') {
              sh 'ansible-playbook roles/sp.yml -i environments -e "target=sta-sp-v4.0 component=monitoring"'
            }
          }
        }
      }
    }
  }
  post {
    success {
      emailext(subject: "SUCCESS: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'", body: """<p>SUCCESS: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':</p>
                        <p>Check console output at &QUOT;<a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a>&QUOT;</p>""", recipientProviders: [[$class: 'DevelopersRecipientProvider']]) 
    }
    failure {
      emailext(subject: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'", body: """<p>FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':</p>
                        <p>Check console output at &QUOT;<a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a>&QUOT;</p>""", recipientProviders: [[$class: 'DevelopersRecipientProvider']])
      
    }
    
  }
}
