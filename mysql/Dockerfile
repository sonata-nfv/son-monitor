FROM ubuntu:14.04

RUN echo "mysql-server-5.5 mysql-server/root_password password 1234" | sudo debconf-set-selections && \
echo "mysql-server-5.5 mysql-server/root_password_again password 1234" | sudo debconf-set-selections && \
apt-get update && apt-get -y upgrade && \
DEBIAN_FRONTEND=noninteractive apt-get -y install mysql-server-5.5 && \
sed -i "s/.*bind-address.*/bind-address = 0.0.0.0/" /etc/mysql/my.cnf &&\
service mysql restart && \
mysql -uroot -p1234 -e "CREATE DATABASE IF NOT EXISTS monitoring CHARACTER SET UTF8" && \
mysql -uroot -p1234 -e "CREATE USER  monitoringuser@localhost IDENTIFIED BY 'sonata'" && \
mysql -uroot -p1234 -e "GRANT ALL PRIVILEGES ON monitoring.* TO 'monitoringuser'@'localhost'" && \
mysql -uroot -p1234 -e "GRANT ALL PRIVILEGES ON monitoring.* TO 'monitoringuser'@'%' IDENTIFIED BY 'sonata' WITH GRANT OPTION" && \
mysql -uroot -p1234 -e "FLUSH PRIVILEGES"

ADD run.sh /run.sh
RUN chmod 0755 /run.sh
RUN ls -la /*

EXPOSE 3306

CMD ["/run.sh"]
