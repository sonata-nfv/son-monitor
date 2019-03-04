#!/bin/bash

echo "Run Unit tests"

docker exec -i test-son-monitor-manager sh -c "cd /opt/Monitoring && python3 manage.py test api.tests.UsersTestCase"
docker exec -i test-son-monitor-manager sh -c "cd /opt/Monitoring && python3 manage.py test api.tests.ApisTestCase"