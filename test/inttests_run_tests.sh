#!/bin/bash

echo "Run Integration tests"
docker exec -i test-son-monitor-manager sh -c "cd /opt/Monitoring && python manage.py test api.tests.IntTestCase"
