from ..settings import LOGGING
from ..httpclient.client import Client
import logging.config
import urllib3, json, os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class Vim(object):
    """Description of Project class"""

    def __init__(self, token):
        """Constructor of Project class"""
        self.__client = Client(verify_ssl_cert=False)
        self.bearer_token = token
        OSM_COMPONENTS = os.environ.get('OSM_COMPONENTS')
        if OSM_COMPONENTS is None:
            print('NO OSM_COMPONENTS in ENV')
        else:
            self.OSM_COMPONENTS = json.loads(OSM_COMPONENTS)

    def get_list(self):
        """Get the list of the registered VIMs in OSM r4

        Returns:
            obj: a requests object

        Examples:
            >>> from nbiapi.identity import bearer_token
            >>> from nbiapi.vim import Vim
            >>> from settings import OSM_ADMIN_CREDENTIALS
            >>> token = bearer_token(OSM_ADMIN_CREDENTIALS.get('username'), OSM_ADMIN_CREDENTIALS.get('username'))
            >>> vim = Vim(token)
            >>> entries = vim.get_list()
            >>> print(entries.json())
        """
        endpoint = '{}/osm/admin/v1/vim_accounts'.format(self.OSM_COMPONENTS.get('NBI-API'))
        headers = {"Authorization": "Bearer {}".format(self.bearer_token), "Accept": "application/json"}
        response = self.__client.get(endpoint, headers)
        return response

    def get(self, vim_uuid=None):
        """Get details for a VIM in OSM r4 by given VIM UUID

        Returns:
            obj: a requests object

        Examples:
            >>> from nbiapi.identity import bearer_token
            >>> from nbiapi.vim import Vim
            >>> from settings import OSM_ADMIN_CREDENTIALS
            >>> token = bearer_token(OSM_ADMIN_CREDENTIALS.get('username'), OSM_ADMIN_CREDENTIALS.get('username'))
            >>> vim = Vim(token)
            >>> vim_account = vim.get("41dab0c0-35f4-4c40-b1cd-13e4a79dab48")
            >>> print(vim_account.json())
        """
        endpoint = '{}/osm/admin/v1/vim_accounts/{}'.format(self.OSM_COMPONENTS.get('NBI-API'), vim_uuid)
        headers = {"Authorization": "Bearer {}".format(self.bearer_token), "Accept": "application/json"}
        response = self.__client.get(endpoint, headers)
        return response
