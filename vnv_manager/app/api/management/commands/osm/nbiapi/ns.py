from ..settings import LOGGING
from ..httpclient.client import Client
import logging.config
import urllib3, json, os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class Ns(object):
    """NS Class.

    Attributes:
        bearer_token (str): The OSM Authorization Token

    Args:
        token (str): The OSM Authorization Token
    """

    def __init__(self, token):
        """NS LCM Class Constructor."""
        self.__client = Client(verify_ssl_cert=False)
        self.bearer_token = token
        OSM_COMPONENTS = os.environ.get('OSM_COMPONENTS')
        if OSM_COMPONENTS is None:
            print('NO OSM_COMPONENTS in ENV')
        else:
            self.OSM_COMPONENTS = json.loads(OSM_COMPONENTS)

    def get_list(self):
        """Fetch a list of all NS Instances

        Returns:
            object: A list of NSs as a requests object

        Examples:
            >>> from nbiapi.identity import bearer_token
            >>> from nbiapi.ns import Ns
            >>> from settings import OSM_ADMIN_CREDENTIALS
            >>> token = bearer_token(OSM_ADMIN_CREDENTIALS.get('username'), OSM_ADMIN_CREDENTIALS.get('username'))
            >>> ns = Ns(token)
            >>> response = ns.get_list()
            >>> print(response.json())

        OSM Cli:
            $ osm ns-list
        """
        endpoint = '{}/osm/nslcm/v1/ns_instances'.format(self.OSM_COMPONENTS.get('NBI-API'))
        headers = {"Authorization": "Bearer {}".format(self.bearer_token), "Accept": "application/json"}
        response = self.__client.get(endpoint, headers)
        logger.debug("Request `GET {}` returns HTTP status `{}`, headers `{}` and body `{}`."
                     .format(response.url, response.status_code, response.headers, response.text))
        return response

    def get(self, ns_uuid=None):
        """Fetch details of a specific NS Instance

        Args:
            ns_uuid (str): The UUID of the NS to fetch details for

        Returns:
            object: A requests object

        Examples:
            >>> from nbiapi.identity import bearer_token
            >>> from nbiapi.ns import Ns
            >>> from settings import OSM_ADMIN_CREDENTIALS
            >>> token = bearer_token(OSM_ADMIN_CREDENTIALS.get('username'), OSM_ADMIN_CREDENTIALS.get('username'))
            >>> ns = Ns(token)
            >>> response = ns.get(ns_uuid='07048175-660b-404f-bbc9-5be7581e74de')

        OSM Cli:
            $ osm ns-show 07048175-660b-404f-bbc9-5be7581e74de
        """
        endpoint = '{}/osm/nslcm/v1/ns_instances/{}'.format(self.OSM_COMPONENTS.get('NBI-API'), ns_uuid)
        headers = {"Authorization": "Bearer {}".format(self.bearer_token), "Accept": "application/json"}
        response = self.__client.get(endpoint, headers)
        logger.debug("Request `GET {}` returns HTTP status `{}`, headers `{}` and body `{}`."
                     .format(response.url, response.status_code, response.headers, response.text))
        return response

    def terminate(self, ns_uuid=None):
        """Terminate a NS Instance.

        Args:
            ns_uuid (str): The UUID of the NS to terminate

        Returns:
            response (object): A requests object

        Examples:
            >>> from nbiapi.identity import bearer_token
            >>> from nbiapi.ns import Ns
            >>> from settings import OSM_ADMIN_CREDENTIALS
            >>> token = bearer_token(OSM_ADMIN_CREDENTIALS.get('username'), OSM_ADMIN_CREDENTIALS.get('username'))
            >>> ns = Ns(token)
            >>> response = ns.terminate(ns_uuid='07048175-660b-404f-bbc9-5be7581e74de')

        """
        endpoint = '{}/osm/nslcm/v1/ns_instances/{}/terminate'.format(self.OSM_COMPONENTS.get('NBI-API'), ns_uuid)
        headers = {"Authorization": "Bearer {}".format(self.bearer_token), "Accept": "application/json"}
        response = self.__client.post(endpoint, headers)
        logger.debug("Request `GET {}` returns HTTP status `{}`, headers `{}` and body `{}`."
                     .format(response.url, response.status_code, response.headers, response.text))
        return response
