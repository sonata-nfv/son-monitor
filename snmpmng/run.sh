#!/bin/bash

python3 /opt/Monitoring/manager.py >/dev/null 2>&1 & \
tail -f /dev/null