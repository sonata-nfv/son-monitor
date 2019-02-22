from ..settings import LOGGING
from ..httpclient.client import Client
import logging.config
import urllib3, json, os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class Vnfd(object):
    """VNF Descriptor Class.

    This class serves as a wrapper for the Virtual Network Function Descriptor (VNFD)
    part of the Northbound Interface (NBI) offered by OSM. The methods defined in this
    class help retrieve the VNFDs of OSM.

    Attributes:
        bearer_token (str): The OSM Authorization Token.

    Args:
        token (str): The OSM Authorization Token.
    """

    def __init__(self, token):
        """VNF Descriptor Class Constructor."""
        self.__client = Client(verify_ssl_cert=False)
        self.bearer_token = token
        OSM_COMPONENTS = os.environ.get('OSM_COMPONENTS')
        if OSM_COMPONENTS is None:
            print('NO OSM_COMPONENTS in ENV')
        else:
            self.OSM_COMPONENTS = json.loads(OSM_COMPONENTS)

    def get_list(self):
        """Fetch a list of the VNF descriptors.

        Returns:
            object: A requests object that includes the list of VNFDs

        Examples:
            >>> from nbiapi.identity import bearer_token
            >>> from nbiapi.vnfd import Vnfd
            >>> from settings import OSM_ADMIN_CREDENTIALS
            >>> token = bearer_token(OSM_ADMIN_CREDENTIALS.get('username'), OSM_ADMIN_CREDENTIALS.get('password'))
            >>> vnfd = Vnfd(token)
            >>> response = vnfd.get_list()

        OSM Cli:
            $ osm vnfd-list
        """
        endpoint = '{}/osm/vnfpkgm/v1/vnf_packages'.format(self.OSM_COMPONENTS.get('NBI-API'))
        headers = {"Authorization": "Bearer {}".format(self.bearer_token), "Accept": "application/json"}
        response = self.__client.get(endpoint, headers)
        logger.debug("Request `GET {}` returns HTTP status `{}`, headers `{}` and body `{}`."
                     .format(response.url, response.status_code, response.headers, response.text))
        return response

    def get(self, vnfd_uuid=None):
        """Fetch details of a specific VNF descriptor.

        Args:
            vnfd_uuid (str): The UUID of the VNFD to fetch details for.

        Returns:
            object: A requests object.

        Examples:
            >>> from nbiapi.identity import bearer_token
            >>> from nbiapi.vnfd import Vnfd
            >>> from settings import OSM_ADMIN_CREDENTIALS
            >>> token = bearer_token(OSM_ADMIN_CREDENTIALS.get('username'), OSM_ADMIN_CREDENTIALS.get('password'))
            >>> vnfd = Vnfd(token)
            >>> response = vnfd.get(vnfd_uuid='89f66f1b-73b5-4dc1-8226-a473a2615627')

        OSM Cli:
            $ osm vnfd-show cirros_vnf
        """
        endpoint = '{}/osm/vnfpkgm/v1/vnf_packages/{}'.format(self.OSM_COMPONENTS.get('NBI-API'), vnfd_uuid)
        headers = {"Authorization": "Bearer {}".format(self.bearer_token), "Accept": "application/json"}
        response = self.__client.get(endpoint, headers)
        logger.debug("Request `GET {}` returns HTTP status `{}`, headers `{}` and body `{}`."
                     .format(response.url, response.status_code, response.headers, response.text))
        return response
