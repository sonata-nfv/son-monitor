FROM alpine:3.8

LABEL maintainer="Panos Karkazis <pkarkazis@synelixis.com>"
# Copy python requirements file
COPY requirements.txt /tmp/requirements.txt

RUN apk add --no-cache \
    python3 \
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

# Custom Supervisord config
COPY supervisord.conf /etc/supervisord.conf

# Copy the Nginx global conf
COPY nginx.conf /etc/nginx/
# Copy the Flask app conf
COPY flask-app.conf /etc/nginx/conf.d/
# Copy the base uWSGI ini file to enable default dynamic uwsgi process number
COPY uwsgi.ini /etc/uwsgi/
# Custom Supervisord config
COPY supervisord.conf /etc/supervisord.conf

# Add demo app
COPY ./app /app
WORKDIR /app


RUN mkdir -p /opt/Monitoring/alertmanager
COPY ./alertmanager-0.15.3.linux-amd64/  /opt/Monitoring/alertmanager/
COPY run.sh /opt/Monitoring/run.sh
RUN chmod 0755 /opt/Monitoring/run.sh

EXPOSE 9093 5001

CMD ["/usr/bin/supervisord","-c","/etc/supervisord.conf"]