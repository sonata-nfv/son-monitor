#!/bin/bash

if [ -d "/opt/Monitoring/prometheus/k8s_cnf" ]; then
  echo "folder found!"
  if [ -f "/opt/Monitoring/prometheus/k8s_cnf/prometheus.yml" ]; then
    rm /opt/Monitoring/prometheus/prometheus.yml
    cp /opt/Monitoring/prometheus/k8s_cnf/prometheus.yml /opt/Monitoring/prometheus/prometheus.yml
    chmod 777 /opt/Monitoring/prometheus/prometheus.yml
  fi
  if [ -e "/opt/Monitoring/prometheus/k8s_cnf/prometheus.rules " ]; then
    cp /opt/Monitoring/prometheus/k8s_cnf/prometheus.rules /opt/Monitoring/prometheus/rules/prometheus.rules
    chmod 777 /opt/Monitoring/prometheus/rules/prometheus.rules
  fi
fi

/opt/Monitoring/prometheus/prometheus --config.file=/opt/Monitoring/prometheus/prometheus.yml --storage.tsdb.path=/prometheus --web.enable-lifecycle --web.console.libraries=/opt/Monitoring/prometheus/console_libraries --web.console.templates=/opt/Monitoring/prometheus/consoles 
