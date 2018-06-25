#!/bin/bash

echo "Deleting old containers"
cnts=$(docker ps --all -q -f network=son-mon-unittests)
if [ "$cnts" != '' ] 
then
   docker rm -fv $cnts
fi

#Creating unittests network
if ! [[ "$(docker network inspect -f {{.Name}} son-mon-unittests 2> /dev/null)" == "" ]]; then docker network rm son-mon-unittests ; fi
docker network create son-mon-unittests

#Run Containers
docker run -d --name test-son-monitor-postgres --net son-mon-unittests --network-alias postgsql -e POSTGRES_DB=monitoring -e POSTGRES_USER=monitoringuser -e POSTGRES_PASSWORD=sonata -e PGPORT=5433  ntboes/postgres-uuid 
docker run -d --name test-son-monitor-influxdb --net son-mon-unittests --network-alias influx -p 8086:8086 registry.sonata-nfv.eu:5000/son-monitor-influxdb
docker run -d -p 5672:5672 -p 8080:15672 --name test-son-broker --net son-mon-unittests --network-alias broker -e RABBITMQ_CONSOLE_LOG=new rabbitmq:3-management
echo "Wait for sqlDB...."
while ! nc -z 127.0.0.1 5433; do
  sleep 1 && echo -n .; # waiting for mysql
done; 
docker run -d --name test-son-monitor-pushgateway --net son-mon-unittests --network-alias pushgateway -p 9091:9091 registry.sonata-nfv.eu:5000/son-monitor-pushgateway
docker run -d --name test-son-monitor-prometheus --net son-mon-unittests --network-alias prometheus -p 9090:9090 -p 9089:9089 -p 8002:8001 -p 8888:8888 -e RABBIT_URL=broker:5672 --add-host ceilometer:192.168.1.127 --add-host manager:192.168.1.127 --add-host pushgateway:192.168.1.127 --add-host influx:192.168.1.127 registry.sonata-nfv.eu:5000/son-monitor-prometheus
docker run -d --name test-son-monitor-manager --net son-mon-unittests --network-alias manager -p 8000:8000 -v /tmp/monitoring/mgr:/var/log/apache2 registry.sonata-nfv.eu:5000/son-monitor-manager




