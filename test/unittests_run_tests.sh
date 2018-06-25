#!/bin/bash

echo "Deleting unittests containers"

docker exec -ti test-son-monitor-manager sh -c "cd /opt/Monitoring && python manage.py test"

