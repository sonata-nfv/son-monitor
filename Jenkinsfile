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
            sh 'docker build -t registry.sonata-nfv.eu:5000/son-monitor-manager -f manager/Dockerfile manager/'
          }
        }
        stage('son-monitor-prometheus') {
          steps {
            sh 'docker build -t registry.sonata-nfv.eu:5000/son-monitor-prometheus -f prometheus/Dockerfile prometheus/'
          }
        }
        stage('son-monitor-pushgateway') {
          steps {
            sh 'docker build -t registry.sonata-nfv.eu:5000/son-monitor-pushgateway -f pushgateway/Dockerfile pushgateway/'
          }
        }
        stage('son-monitor-influxdb') {
          steps {
            sh 'docker build -t registry.sonata-nfv.eu:5000/son-monitor-influxdb -f influxDB/Dockerfile influxDB/'
          }
        }
        stage('son-monitor-snmpmng') {
          steps {
            sh 'docker build -t registry.sonata-nfv.eu:5000/son-monitor-snmpmng -f snmpmng/Dockerfile snmpmng/'
          }
        }
      }
    }
    stage('Unit Tests: Preparation') {
      steps {
        echo 'Prepear for Unit Tests'
        sh './test/unittests_preparation.sh'
      }
    }
    stage('Unit Tests: Execution') {
      steps {
        echo 'Excute Tests'
        sh './test/unittests_run_tests.sh'
      }
    }
    stage('Unit Tests: Clean') {
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
            sh 'docker push registry.sonata-nfv.eu:5000/son-monitor-manager'
          }
        }
        stage('son-monitor-prometheus') {
          steps {
            sh 'docker push registry.sonata-nfv.eu:5000/son-monitor-prometheus'
          }
        }
        stage('son-monitor-pushgateway') {
          steps {
            sh 'docker push registry.sonata-nfv.eu:5000/son-monitor-pushgateway'
          }
        }
        stage('son-monitor-influxdb') {
          steps {
            sh 'docker push registry.sonata-nfv.eu:5000/son-monitor-influxdb'
          }
        }
        stage('son-monitor-snmpmng') {
          steps {
            sh 'docker push registry.sonata-nfv.eu:5000/son-monitor-snmpmng'
          }
        }
      }
    }
    stage('Deployment in pre integration') {
      parallel {
        stage('Deployment in pre integration') {
          steps {
            echo 'Deploying in pre integration...'
          }
        }
        stage('Deploying') {
          steps {
            sh 'rm -rf tng-devops || true'
            sh 'git clone https://github.com/sonata-nfv/tng-devops.git'
            dir(path: 'tng-devops') {
              sh 'ansible-playbook roles/sp.yml -i environments -e "target=pre-int-sp"'
            }
          }
        }
      }
    }
    stage('Promoting containers to integration env') {
      when {
         branch 'master'
      }
      parallel {
        stage('Publishing containers to int') {
          steps {
            echo 'Promoting containers to integration'
          }
        }
        stage('son-monitor-manager') {
          steps {
            sh 'docker tag registry.sonata-nfv.eu:5000/son-monitor-manager:latest registry.sonata-nfv.eu:5000/son-monitor-manager:int'
            sh 'docker push  registry.sonata-nfv.eu:5000/son-monitor-manager:int'
          }
        }
        stage('son-monitor-prometheus') {
          steps {
            sh 'docker tag registry.sonata-nfv.eu:5000/son-monitor-prometheus:latest registry.sonata-nfv.eu:5000/son-monitor-prometheus:int'
            sh 'docker push  registry.sonata-nfv.eu:5000/son-monitor-prometheus:int'
          }
        }
        stage('son-monitor-pushgateway') {
          steps {
            sh 'docker tag registry.sonata-nfv.eu:5000/son-monitor-pushgateway:latest registry.sonata-nfv.eu:5000/son-monitor-pushgateway:int'
            sh 'docker push  registry.sonata-nfv.eu:5000/son-monitor-pushgateway:int'
          }
        }
        stage('son-monitor-influxdb') {
          steps {
            sh 'docker tag registry.sonata-nfv.eu:5000/son-monitor-influxdb:latest registry.sonata-nfv.eu:5000/son-monitor-influxdb:int'
            sh 'docker push  registry.sonata-nfv.eu:5000/son-monitor-influxdb:int'
          }
        }
        stage('son-monitor-snmpmng') {
          steps {
            sh 'docker tag registry.sonata-nfv.eu:5000/son-monitor-snmpmng:latest registry.sonata-nfv.eu:5000/son-monitor-snmpmng:int'
            sh 'docker push  registry.sonata-nfv.eu:5000/son-monitor-snmpmng:int'
          }
        }
      }
    }
    stage('Deployment in integration') {
      when {
         branch 'master'
      }
      parallel {
        stage('Deployment in integration') {
          steps {
            echo 'Deploying in integration...'
          }
        }
        stage('Deploying') {
          steps {
            sh 'rm -rf tng-devops || true'
            sh 'git clone https://github.com/sonata-nfv/tng-devops.git'
            dir(path: 'tng-devops') {
              sh 'ansible-playbook roles/sp.yml -i environments -e "target=int-sp"'
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