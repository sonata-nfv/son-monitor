from ..settings import LOGGING
from ..httpclient.client import Client
import logging.config
import urllib3, json, os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class User(object):
    """Description of User class"""

    def __init__(self, token):
        """Constructor of User class"""
        self.__client = Client(verify_ssl_cert=False)
        self.bearer_token = token
        OSM_COMPONENTS = os.environ.get('OSM_COMPONENTS')
        if OSM_COMPONENTS is None:
            print('NO OSM_COMPONENTS in ENV')
        else:
            self.OSM_COMPONENTS = json.loads(OSM_COMPONENTS)

    def get_list(self):
        """Get the list of the registered users in OSM r4

        Returns:
            obj: a requests object

        Examples:
            >>> from nbiapi.identity import bearer_token
            >>> from nbiapi.user import User
            >>> from settings import OSM_ADMIN_CREDENTIALS
            >>> token = bearer_token(OSM_ADMIN_CREDENTIALS.get('username'), OSM_ADMIN_CREDENTIALS.get('username'))
            >>> user = User(token)
            >>> response = user.get_list()
            >>> print(response.json())
        """
        endpoint = '{}/osm/admin/v1/users'.format(self.OSM_COMPONENTS.get('NBI-API'))
        headers = {"Authorization": "Bearer {}".format(self.bearer_token), "Accept": "application/json"}
        response = self.__client.get(endpoint, headers)
        return response

    def get(self, username=None):
        """Get details of a user in OSM r4 by given username

        Returns:
            obj: a requests object

        Examples:
            >>> from nbiapi.identity import bearer_token
            >>> from nbiapi.user import User
            >>> from settings import OSM_ADMIN_CREDENTIALS
            >>> token = bearer_token(OSM_ADMIN_CREDENTIALS.get('username'), OSM_ADMIN_CREDENTIALS.get('username'))
            >>> user = User(token)
            >>> response = user.get(username="admin")
            >>> print(response.json())
        """
        endpoint = '{}/osm/admin/v1/users/{}'.format(self.OSM_COMPONENTS.get('NBI-API'), username)
        headers = {"Authorization": "Bearer {}".format(self.bearer_token), "Accept": "application/json"}
        response = self.__client.get(endpoint, headers)
        return response
