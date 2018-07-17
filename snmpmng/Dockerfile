FROM python:3.6-jessie

RUN apt-get update && apt-get -y upgrade && \
apt-get -y install apache2 python3 libmysqlclient-dev python3-dev python3-setuptools nano vim && \ 
mkdir -p /opt/Monitoring

COPY ./ /opt/Monitoring
RUN pip3 install -r /opt/Monitoring/requirements.txt

ADD ./run.sh /opt/Monitoring/run.sh
RUN chmod 0755 /opt/Monitoring/run.sh
RUN ls -la /opt/Monitoring/*

CMD ["/opt/Monitoring/run.sh"]
