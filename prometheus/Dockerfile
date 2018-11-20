FROM alpine:3.8

LABEL maintainer="Panos Karkazis <pkarkazis@synelixis.com>"

# Copy python requirements file
COPY requirements.txt /tmp/requirements.txt

RUN apk add --no-cache \
    python3 \
    bash \
    nginx \
    uwsgi \
    uwsgi-python3 \
    supervisor \
    py-yaml \
    py-httplib2 \ 
    nano \
    curl && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    pip3 install -r /tmp/requirements.txt && \
    rm /etc/nginx/conf.d/default.conf && \
    rm -r /root/.cache

# Copy the Nginx global conf
COPY nginx.conf /etc/nginx/
# Copy the Flask Nginx site conf
COPY flask-app.conf /etc/nginx/conf.d/
# Copy the base uWSGI ini file to enable default dynamic uwsgi process number
COPY uwsgi.ini /etc/uwsgi/
# Custom Supervisord config
COPY supervisord.conf /etc/supervisord.conf

# Add demo app
COPY ./app /app
WORKDIR /app

RUN mkdir -p /opt/Monitoring/prometheus
COPY ./prometheus-2.4.3.linux-amd64/ /opt/Monitoring/prometheus
COPY run.sh /opt/Monitoring/run.sh
RUN chmod 0755 /opt/Monitoring/run.sh
RUN chmod -R 0777 /opt/Monitoring/prometheus



EXPOSE     9090 9089 8002
VOLUME     [ "/prometheus" ]


CMD ["/usr/bin/supervisord"]
