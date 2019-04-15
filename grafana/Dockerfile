FROM grafana/grafana:6.0.2

USER root

ENV GF_AUTH_ANONYMOUS_ENABLED=true

ADD ./datasources/ /etc/grafana/provisioning/datasources/
ADD ./dashboards/ /etc/grafana/provisioning/dashboards/

RUN ls -la /etc/grafana/provisioning/datasources/
RUN ls -la /etc/grafana/provisioning/dashboards/


#RUN mkdir -p /opt/conf
#COPY ./ /opt/conf
#RUN ls -la /opt/conf

#RUN chmod 0755 /opt/conf/*.sh

EXPOSE 3000

#WORKDIR /opt/conf
#RUN echo "/opt/conf/configure.sh" >> /run.sh
#RUN cat /run.sh
