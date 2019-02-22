from ..settings import LOGGING
from ..httpclient.client import Client
import logging.config
import urllib3, json, os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class Vnf(object):
    """VNF Class.

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
        """Fetch a list of all VNFs.

        Returns:
            object: A requests object

        Examples:
            >>> from nbiapi.identity import bearer_token
            >>> from nbiapi.vnf import Vnf
            >>> from settings import OSM_ADMIN_CREDENTIALS
            >>> token = bearer_token(OSM_ADMIN_CREDENTIALS.get('username'), OSM_ADMIN_CREDENTIALS.get('username'))
            >>> vnf = Vnf(token)
            >>> response = vnf.get_list()

        OSM Cli:
            $ osm vnf-list
        """
        endpoint = '{}/osm/nslcm/v1/vnf_instances'.format(self.OSM_COMPONENTS.get('NBI-API'))
        headers = {"Authorization": "Bearer {}".format(self.bearer_token), "Accept": "application/json"}
        response = self.__client.get(endpoint, headers)
        logger.debug("Request `GET {}` returns HTTP status `{}`, headers `{}` and body `{}`."
                     .format(response.url, response.status_code, response.headers, response.text))
        return response

    def get_list_by_ns(self, ns_uuid=None):
        """Fetch list of VNFs for specific NS Instance.

        Args:
            ns_uuid (str): The UUID of the NS to fetch VNFs for.

        Returns:
            object: A requests object.

        Examples:
            >>> from nbiapi.identity import bearer_token
            >>> from nbiapi.vnf import Vnf
            >>> from settings import OSM_ADMIN_CREDENTIALS
            >>> token = bearer_token(OSM_ADMIN_CREDENTIALS.get('username'), OSM_ADMIN_CREDENTIALS.get('username'))
            >>> vnf = Vnf(token)
            >>> response = vnf.get_list_by_ns(ns_uuid='a5f506e9-45c7-42fd-b12d-b5c657ed87fb')

        """
        endpoint = '{}/osm/nslcm/v1/vnf_instances?nsr-id-ref={}'.format(self.OSM_COMPONENTS.get('NBI-API'), ns_uuid)
        headers = {"Authorization": "Bearer {}".format(self.bearer_token), "Accept": "application/json"}
        response = self.__client.get(endpoint, headers)
        logger.debug("Request `GET {}` returns HTTP status `{}`, headers `{}` and body `{}`."
                     .format(response.url, response.status_code, response.headers, response.text))
        return response

    def get(self, vnf_uuid=None):
        """Fetch details of a specific VNF

        Args:
            vnf_uuid (str): The UUID of the VNF to fetch details for

        Returns:
            object: A requests object

        Examples:
            >>> from nbiapi.identity import bearer_token
            >>> from nbiapi.vnf import Vnf
            >>> from settings import OSM_ADMIN_CREDENTIALS
            >>> token = bearer_token(OSM_ADMIN_CREDENTIALS.get('username'), OSM_ADMIN_CREDENTIALS.get('username'))
            >>> vnf = Vnf(token)
            >>> response = vnf.get(vnf_uuid='a5f506e9-45c7-42fd-b12d-b5c657ed87fb')

        OSM Cli:
            $ osm vnf-show a5f506e9-45c7-42fd-b12d-b5c657ed87fb
        """
        endpoint = '{}/osm/nslcm/v1/vnf_instances/{}'.format(self.OSM_COMPONENTS.get('NBI-API'), vnf_uuid)
        headers = {"Authorization": "Bearer {}".format(self.bearer_token), "Accept": "application/json"}
        response = self.__client.get(endpoint, headers)
        logger.debug("Request `GET {}` returns HTTP status `{}`, headers `{}` and body `{}`."
                     .format(response.url, response.status_code, response.headers, response.text))
        return response
