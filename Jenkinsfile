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
        stage('son-vnv_monitor-manager') {
          steps {
            sh 'docker build -t registry.sonata-nfv.eu:5000/son-vnv-monitor-manager -f vnv_manager/Dockerfile vnv_manager/'
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
        stage('son-monitor-alertmanager') {
          steps {
            sh 'docker build -t registry.sonata-nfv.eu:5000/son-monitor-alertmanager -f alertmanager/Dockerfile alertmanager/'
          }
        }
        stage('son-monitor-snmpmng') {
          steps {
            sh 'docker build -t registry.sonata-nfv.eu:5000/son-monitor-snmpmng -f snmpmng/Dockerfile snmpmng/'
          }
        }
        stage('son-monitor-grafana') {
          steps {
            sh 'docker build -t registry.sonata-nfv.eu:5000/son-monitor-grafana -f grafana/Dockerfile grafana/'
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
            sh 'docker push registry.sonata-nfv.eu:5000/son-monitor-manager'
          }
        }
        stage('son-vnv-monitor-manager') {
          steps {
            sh 'docker push registry.sonata-nfv.eu:5000/son-vnv-monitor-manager'
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
        stage('son-monitor-alertmanager') {
          steps {
            sh 'docker push registry.sonata-nfv.eu:5000/son-monitor-alertmanager'
          }
        }
        stage('son-monitor-snmpmng') {
          steps {
            sh 'docker push registry.sonata-nfv.eu:5000/son-monitor-snmpmng'
          }
        }
        stage('son-monitor-grafana') {
          steps {
            sh 'docker push registry.sonata-nfv.eu:5000/son-monitor-grafana'
          }
        }
      }
    }
    stage('Deployment in SP pre-int') {
      parallel {
        stage('Deployment in SP pre-int') {
          steps {
            echo 'Deploying in pre-int...'
          }
        }
        stage('Deploying in SP') {
          steps {
            sh 'rm -rf tng-devops || true'
            sh 'git clone https://github.com/sonata-nfv/tng-devops.git'
            dir(path: 'tng-devops') {
              sh 'ansible-playbook roles/sp.yml -i environments -e "target=pre-int-sp component=monitoring"'
            }
          }
        }
      }
    }
    stage('Deployment in VnV pre-int') {
      parallel {
        stage('Deployment in VnV pre-int') {
          steps {
            echo 'Deploying in pre-int...'
          }
        }
        stage('Deploying in VnV') {
          steps {
            sh 'rm -rf tng-devops || true'
            sh 'git clone https://github.com/sonata-nfv/tng-devops.git'
            dir(path: 'tng-devops') {
              sh 'ansible-playbook roles/vnv.yml -i environments -e "target=pre-int-vnv-bcn.5gtango.eu component=monitoring"'
            }
          }
        }
      }
    }
    stage('Promoting containers to integration env') {
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
        stage('son-vnv-monitor-manager') {
          steps {
            sh 'docker tag registry.sonata-nfv.eu:5000/son-vnv-monitor-manager:latest registry.sonata-nfv.eu:5000/son-vnv-monitor-manager:int'
            sh 'docker push  registry.sonata-nfv.eu:5000/son-vnv-monitor-manager:int'
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
        stage('son-monitor-alertmanager') {
          steps {
            sh 'docker tag registry.sonata-nfv.eu:5000/son-monitor-alertmanager:latest registry.sonata-nfv.eu:5000/son-monitor-alertmanager:int'
            sh 'docker push  registry.sonata-nfv.eu:5000/son-monitor-alertmanager:int'
          }
        }
        stage('son-monitor-snmpmng') {
          steps {
            sh 'docker tag registry.sonata-nfv.eu:5000/son-monitor-snmpmng:latest registry.sonata-nfv.eu:5000/son-monitor-snmpmng:int'
            sh 'docker push  registry.sonata-nfv.eu:5000/son-monitor-snmpmng:int'
          }
        }
        stage('son-monitor-grafana') {
          steps {
            sh 'docker tag registry.sonata-nfv.eu:5000/son-monitor-grafana:latest registry.sonata-nfv.eu:5000/son-monitor-grafana:int'
            sh 'docker push  registry.sonata-nfv.eu:5000/son-monitor-grafana:int'
          }
        }
      }
    }
    stage('Deployment in SP integration') {
      parallel {
        stage('Deployment in SP integration') {
          steps {
            echo 'Deploying in integration...'
          }
        }
        stage('Deploying in SP') {
          steps {
            sh 'rm -rf tng-devops || true'
            sh 'git clone https://github.com/sonata-nfv/tng-devops.git'
            dir(path: 'tng-devops') {
              sh 'ansible-playbook roles/sp.yml -i environments -e "target=int-sp component=monitoring"'
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
