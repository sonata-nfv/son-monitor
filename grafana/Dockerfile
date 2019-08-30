FROM grafana/grafana:6.0.2 AS mon-grafana

USER root

ENV GF_AUTH_ANONYMOUS_ENABLED=true
ENV GF_LOG_MODE=file

EXPOSE 3000

FROM  mon-grafana AS mon-sp-grafana
ADD ./datasources/ /etc/grafana/provisioning/datasources/
ADD ./dashboards/sp/ /etc/grafana/provisioning/dashboards/
RUN ls -la /etc/grafana/provisioning/datasources/
RUN ls -la /etc/grafana/provisioning/dashboards/

FROM  mon-grafana AS mon-vnv-grafana
ADD ./datasources/ /etc/grafana/provisioning/datasources/
ADD ./dashboards/vnv/ /etc/grafana/provisioning/dashboards/
RUN ls -la /etc/grafana/provisioning/datasources/
RUN ls -la /etc/grafana/provisioning/dashboards/
