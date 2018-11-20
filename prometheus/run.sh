#!/bin/bash

/opt/Monitoring/prometheus/prometheus --config.file=/opt/Monitoring/prometheus/prometheus.yml --storage.tsdb.path=/prometheus --web.enable-lifecycle --web.console.libraries=/opt/Monitoring/prometheus/console_libraries --web.console.templates=/opt/Monitoring/prometheus/consoles 
