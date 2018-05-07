FROM influxdb:0.13.0

RUN mkdir /opt/influxDB
ADD influxdb.conf /etc/influxdb/influxdb.conf
ADD run.sh /opt/influxDB/run.sh
RUN chmod 0755 /opt/influxDB/run.sh
RUN ls -la /opt/influxDB/*

EXPOSE 8086

CMD ["/opt/influxDB/run.sh"]

