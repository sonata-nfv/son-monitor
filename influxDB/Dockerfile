FROM influxdb:1.5

RUN mkdir /opt/influxDB
ADD run.sh /opt/influxDB/run.sh
RUN chmod 0755 /opt/influxDB/run.sh
RUN ls -la /opt/influxDB/*

EXPOSE 8086

VOLUME /var/lib/influxdb

CMD ["/opt/influxDB/run.sh"]

