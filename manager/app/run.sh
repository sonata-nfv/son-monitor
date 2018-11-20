#!/bin/bash
echo "Wait for sqlDB...."
while ! nc -z son-monitor-postgres 5433; do
  sleep 1 && echo -n .; # waiting for mysql
done; 
python /opt/Monitoring/manage.py makemigrations && \
python /opt/Monitoring/manage.py migrate && \
python /opt/Monitoring/manage.py loaddata /opt/Monitoring/db_data.json && \
python /opt/Monitoring/manage.py collectstatic --noinput && \
var=$(echo "from django.contrib.auth.models import User; User.objects.filter(username='user').exists()" |  python /opt/Monitoring/manage.py shell) && \
if [[ $var == *"False"* ]]
then
 echo "from django.contrib.auth.models import User; User.objects.create_superuser('user', 'user@mail.com', 'sonat@')" |  python /opt/Monitoring/manage.py shell 
fi && \
tail -f /dev/null
