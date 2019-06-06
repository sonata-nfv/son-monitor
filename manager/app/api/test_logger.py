import logging
from Logger import TangoLogger

LOG = TangoLogger.getLogger("son-monitor-manager", log_level=logging.INFO, log_json=True)

LOG.warning("this is a test message")
LOG.warning("this is a test message", extra={"start_stop": "START", "status": "201"})


