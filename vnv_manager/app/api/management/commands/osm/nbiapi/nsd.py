from ..settings import LOGGING
from ..httpclient.client import Client
import logging.config
import urllib3, json, os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class Nsd(object):
    """NS Descriptor Class.

    This class serves as a wrapper for the Network Service Descriptor (NSD) part
    of the Northbound Interface (NBI) offered by OSM r4. The methods defined in this
    class help retrieve the NSDs of OSM.

    Attributes:
        bearer_token (str): The OSM Authorization Token.

    Args:
        token (str): The OSM Authorization Token.

    """

    def __init__(self, token):
        """NS Descriptor Class Constructor."""
        self.__client = Client(verify_ssl_cert=False)
        self.bearer_token = token
        OSM_COMPONENTS = os.environ.get('OSM_COMPONENTS')
        if OSM_COMPONENTS is None:
            print('NO OSM_COMPONENTS in ENV')
        else:
            self.OSM_COMPONENTS = json.loads(OSM_COMPONENTS)

    def get_list(self):
        '''
        Fetch a list of all NS descriptors.

        Returns:
            object: A requests object including the list of the NSDs

        Examples:
            >>> from nbiapi.identity import bearer_token
            >>> from nbiapi.nsd import Nsd
            >>> from settings import OSM_ADMIN_CREDENTIALS
            >>> token = bearer_token(OSM_ADMIN_CREDENTIALS.get('username'), OSM_ADMIN_CREDENTIALS.get('username'))
            >>> nsd = Nsd(token)
            >>> response = nsd.get_list()
            >>> print(response.status_code)
            200

        OSM Cli:
            $ osm nsd-list
        '''
        endpoint = '{}/osm/nsd/v1/ns_descriptors'.format(self.OSM_COMPONENTS.get('NBI-API'))
        headers = {"Authorization": "Bearer {}".format(self.bearer_token), "Accept": "application/json"}
        response = self.__client.get(endpoint, headers)
        logger.debug("Request `GET {}` returns HTTP status `{}`, headers `{}` and body `{}`."
                     .format(response.url, response.status_code, response.headers, response.text))
        return response

    def get(self, nsd_uuid=None):
        """Fetch details of a specific NS descriptor.

        Args:
            nsd_uuid (str): The UUID of the NSD to fetch details for.

        Returns:
            object: A requests object including the NSD

        Examples:
            >>> from nbiapi.identity import bearer_token
            >>> from nbiapi.nsd import Nsd
            >>> from settings import OSM_ADMIN_CREDENTIALS
            >>> token = bearer_token(OSM_ADMIN_CREDENTIALS.get('username'), OSM_ADMIN_CREDENTIALS.get('username'))
            >>> nsd = Nsd(token)
            >>> response = nsd.get(nsd_uuid='9c4a8f58-8317-40a1-b9fe-1db18cff6965')

        OSM Cli:
            $ osm nsd-show cirros_2vnf_ns
        """
        endpoint = '{}/osm/nsd/v1/ns_descriptors/{}'.format(self.OSM_COMPONENTS.get('NBI-API'), nsd_uuid)
        headers = {"Authorization": "Bearer {}".format(self.bearer_token), "Accept": "application/json"}
        response = self.__client.get(endpoint, headers)
        logger.debug("Request `GET {}` returns HTTP status `{}`, headers `{}` and body `{}`."
                     .format(response.url, response.status_code, response.headers, response.text))
        return response
