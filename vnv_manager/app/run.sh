#!/bin/bash
echo "Wait for sqlDB...."
while ! nc -z son-monitor-postgres 5433; do
  sleep 1 && echo -n .; # waiting for mysql
done; 
python3 /opt/Monitoring/manage.py makemigrations api && \
python3 /opt/Monitoring/manage.py migrate api && \
python3 /opt/Monitoring/manage.py loaddata /opt/Monitoring/db_data.json && \
python3 /opt/Monitoring/manage.py collectstatic --noinput && \
var=$(echo "from django.contrib.auth.models import User; User.objects.filter(username='user').exists()" |  python3 /opt/Monitoring/manage.py shell) && \
if [[ $var == *"False"* ]]
then
 echo "from django.contrib.auth.models import User; User.objects.create_superuser('user', 'user@mail.com', 'sonat@')" |  python3 /opt/Monitoring/manage.py shell 
fi && \
#cp /opt/Monitoring/apache-site /etc/apache2/sites-available/000-default.conf && \
#sed -i.bak 's/.*Listen.*/Listen '8000'/' /etc/apache2/ports.conf && \
#chown -R www-data:www-data /opt/Monitoring && \
#python /opt/Monitoring/manage.py runserver 0.0.0.0:8000 && \
#service apache2 restart
tail -f /dev/null
