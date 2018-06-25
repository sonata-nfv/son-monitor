#!/bin/bash

echo "Run Unit tests"

docker exec -i test-son-monitor-manager sh -c "cd /opt/Monitoring && python manage.py test"


echo "Monitoring Manager unittests finised"