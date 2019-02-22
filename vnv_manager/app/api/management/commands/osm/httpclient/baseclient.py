import abc


class AbstractClient(object):
    """Abstract operations of HTTP client"""

    def __init__(self):
        pass

    def list(self, url, headers, **kwargs):
        """Fetch the list of entities"""
        pass

    def get(self, url, headers, **kwargs):
        """Fetch a list of entities or an entity"""
        pass

    def post(self, url, headers, payload, **kwargs):
        """Insert an entity"""
        pass

    def put(self, url, headers, payload, **kwargs):
        """Update partially an entity"""
        pass
