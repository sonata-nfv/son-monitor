#!/bin/bash

echo "Run Unit tests"
docker exec -i test-son-monitor-manager sh -c "cd /opt/Monitoring && python3 manage.py test api.tests.UsersTestCase.setUp"
echo "Check DB connectivity"
docker exec -i test-son-monitor-manager sh -c "cd /opt/Monitoring && python3 manage.py test api.tests.UsersTestCase.test_user_email"

echo "Run API tests"
docker exec -i test-son-monitor-manager sh -c "cd /opt/Monitoring && python3 manage.py test api.tests.ApisTestCase"