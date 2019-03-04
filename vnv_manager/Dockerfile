FROM alpine:3.8

LABEL maintainer "Panos Karkazis <pkarkazis@synelixis.com>"


# Copy python requirements file
COPY ./app/requirements.txt /tmp/requirements.txt

RUN apk add --no-cache \
    python3 \
    yaml-dev \
    python3-dev \
    py-requests \
    postgresql-dev \
    libevent-dev \
    gcc \
    musl-dev \
    linux-headers \
    bash \
    nginx \
    uwsgi \
    uwsgi-python3 \
    supervisor && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    pip3 install -r /tmp/requirements.txt && \
    rm /etc/nginx/conf.d/default.conf && \
    rm -r /root/.cache


RUN mkdir -p /opt/Monitoring
RUN mkdir -p /run/nginx
# Add application
COPY ./app /opt/Monitoring

RUN chmod 0755 /opt/Monitoring/run.sh



# Copy the Nginx global conf
COPY nginx.conf /etc/nginx/nginx.conf
# Copy the Flask Nginx site conf
COPY django-app.conf /etc/nginx/conf.d/django-app.conf 
# Copy the base uWSGI ini file to enable default dynamic uwsgi process number
COPY uwsgi.ini /etc/uwsgi/uwsgi.ini
# Custom Supervisord config
COPY supervisord.conf /etc/supervisord.conf


WORKDIR /opt/Monitoring
#CMD ["/opt/Monitoring/run.sh"]

CMD ["supervisord", "-n", "-c", "/etc/supervisord.conf"]