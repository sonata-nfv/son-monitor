FROM ubuntu:14.04

RUN apt-get update && apt-get -y upgrade && \
apt-get -y install apache2 python2.7 python-pip libmysqlclient-dev python2.7-dev libyaml-dev libapache2-mod-wsgi 

RUN mkdir /opt/Monitoring
COPY ./ /opt/Monitoring
RUN ls -la /opt/Monitoring/*

RUN pip install -r /opt/Monitoring/requirements.txt
#service mysql restart && \
#python /opt/Monitoring/manager/manage.py makemigrations && \
#python /opt/Monitoring/manager/manage.py migrate && \
#echo "from django.contrib.auth.models import User; User.objects.create_superuser('user', 'user@mail.com', 'sonat@')" | python /opt/Monitoring/manager/manage.py shell


ADD ./run.sh /opt/Monitoring/run.sh
RUN chmod 0755 /opt/Monitoring/run.sh
RUN ls -la /opt/Monitoring/*

EXPOSE 8000 9000 9090

CMD ["/opt/Monitoring/run.sh"]
