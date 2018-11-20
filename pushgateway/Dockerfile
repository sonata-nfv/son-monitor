FROM  debian:jessie-slim
LABEL maintainer="Panos Karkazis <pkarkazis@synelixis.com>"


RUN mkdir -p /opt/Monitoring/pushgateway
COPY ./ /opt/Monitoring/pushgateway/

ADD run.sh /opt/Monitoring/run.sh
RUN chmod 0755 /opt/Monitoring/run.sh

RUN ls -la /opt/Monitoring/*

WORKDIR /opt/Monitoring/pushgateway/

EXPOSE 9091

ENTRYPOINT [ "/opt/Monitoring/pushgateway/pushgateway" ]


