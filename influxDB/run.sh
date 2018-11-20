#!/bin/bash
influxd &>/dev/nul &
sleep 5 &&  curl -G http://localhost:8086/query --data-urlencode "q=CREATE DATABASE prometheus"

tail -f /dev/null

