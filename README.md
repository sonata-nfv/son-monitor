[![Build Status](http://jenkins.sonata-nfv.eu/buildStatus/icon?job=son-monitor-pipeline/master)](http://jenkins.sonata-nfv.eu/job/son-monitor-pipeline/master)
<p align="center"><img src="https://github.com/sonata-nfv/son-monitor/wiki/images/sonata-5gtango-logo-500px.png" /></p>

# Monitoring Framework
[5GTango](http://5gtango.eu)/[Sonata](http://sonata-nfv.eu) monitoring system gathers and analyzes performance information from network service (NS) and Virtual Network Functions (VNF) and provides alarm notifications, based on rule definitions which are defined by the users. The architecture of the system is based on data exporters and a monitoring server. Data exporters send monitoring data from NS and respective VNF to monitoring server which collects, analyses and stores data and generates the appropriate notifications in case of rule violations. In general, monitoring server consists of a RESTful API interface, an alerting mechanism, a timeseries database and a set of convenient notification services, including a pub/sub based message bus, SMS, email, etc.


## Development
SONATA's monitoring system is based on following services:

1. [Monitoring manager](https://github.com/sonata-nfv/son-monitor/tree/master/manager): Is a Django/rest-framework server combined with a relational database (mysql,postgres ect). Monitoring manager relates each metric in Prometheus DB with Sonata's monitored entities like NS/VNFs, VMs and VIMs.

2. [Prometheus server](https://github.com/sonata-nfv/son-monitor/tree/master/prometheus): Prometheus is an open-source systems monitoring and alerting toolkit, its a standalone server not depending on network storage or other remote services. 

3. [Prometheus pushgateway](https://github.com/sonata-nfv/son-monitor/tree/master/pushgateway): Despite the fact that the default approach from prometheus is to retrieve the metrics data by performing http get requests to exporters (containers, vms etc). The usage of http post methods from exporters to Prometheus has many advantages like no need for exporters to implement a web socket in order to be reached from prometheus. So, there is no need to reconfigure prometheus each time a VNF is created or changes ip address etc.

4. [SNMP manager](https://github.com/sonata-nfv/son-monitor/tree/master/snmpmng): Monitoring framwork provides a mechanism (based on SNMP protocol) in order to collect metrics from vnfs which supports this fuctionatily. The needed snmp information (ex. port, oids, metric names etc) are defined from the inside the vnf descriptor.  

### Building
Each micro service of the framework is executed in its own Docker container. Building steps are defined in a Dockerfile of each service
```
docker build -f pushgatwway/Dockerfile -t registry.sonata-nfv.eu:5000/son-monitor-pushgateway .
docker build -f prometheus/Dockerfile -t registry.sonata-nfv.eu:5000/son-monitor-prometheus .
docker build -f manager/Dockerfile -t registry.sonata-nfv.eu:5000/son-monitor-manager .
docker build -f snmpmng/Dockerfile -t registry.sonata-nfv.eu:5000/son-monitor-snmpmng .
```

### Dependencies
 * docker-compose==1.6.2 (Apache 2.0)
 * Django==1.9.2 (BSD)
 * django-filter==0.12.0 (BSD)
 * django-rest-multiple-models==1.6.3 (MIT)
 * django-rest-swagger==0.3.5 (BSD)
 * djangorestframework==3.3.2 (BSD)
 * django-cors-headers==1.1.0 (MIT)
 * Markdown==2.6.5 (BSD)
 * Pygments==2.1.1 (BSD)
 * PyYAML==3.11 (MIT)
 * Prometheus==0.17 (Apache 2.0)
 * Pushgateway==0.2.0 (Apache 2.0)

### Contributing
To contribute to the development of the 5GTango/SONATA monitoring framwork you have to fork the repository, commit new code and create pull requests.

## Installation
```
docker run -d --name son-monitor-influxdb -p 8086:8086 registry.sonata-nfv.eu:5000/son-monitor-influxdb
docker run -d --name son-monitor-postgres -e POSTGRES_DB=dbname -e POSTGRES_USER=user -e POSTGRES_PASSWORD=pass -p 5433:5432 ntboes/postgres-uuid
docker run -d --name son-monitor-pushgateway -p 9091:9091 registry.sonata-nfv.eu:5000/son-monitor-pushgateway
docker run -d --name son-monitor-prometheus -p 9090:9090 -p 9089:9089 -e RABBIT_URL=<son-broker-ip>:5671 --add-host pushgateway:127.0.0.1 --add-host influx:127.0.0.1 registry.sonata-nfv.eu:5000/son-monitor-prometheus
docker run -d --name son-monitor-manager --add-host postgsql:127.0.0.1 --add-host prometheus:127.0.0.1 -p 8000:8000 registry.sonata-nfv.eu:5000/son-monitor-manager
docker run -d --name son-monitor-snmpmng -e POSTGS_PORT=<postgres_port> -e POSTGS_HOST=<postgres_ip> -e DB_USER_NAME=<user_name> -e DB_USER_PASS=<password> -e PROM_SRV=[\"<pushgateway_url>\"]  registry.sonata-nfv.eu:5000/son-monitor-snmpmng
```

## Usage
Documentation of the RESTful API of Monitoring Manager is provided by a Swagger UI from each instance of the [Monitoring Manager](http://127.0.0.1:8000/docs) and also in [5GTango documantation page](https://sonata-nfv.github.io/tng-doc/).

## License
Monitoring framework is published under Apache 2.0 license. Please see the LICENSE file for more details.

#### Lead Developers

The following lead developers are responsible for this repository and have admin rights. They can, for example, merge pull requests.
 
 * Panos Trakadas (trakadasp)
 * Panos Karkazis (pkarkazis)

#### Feedback-Chanel

* Please use the GitHub issues to report bugs.
