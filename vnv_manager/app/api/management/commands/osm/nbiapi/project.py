from ..settings import LOGGING
from ..httpclient.client import Client
import logging.config
import urllib3,json,os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class Project(object):
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
        """Get the list of the registered Projects in OSM r4

        Returns:
            obj: a requests object

        Examples:
            >>> from nbiapi.identity import bearer_token
            >>> from nbiapi.project import Project
            >>> from settings import OSM_ADMIN_CREDENTIALS
            >>> token = bearer_token(OSM_ADMIN_CREDENTIALS.get('username'), OSM_ADMIN_CREDENTIALS.get('username'))
            >>> project = Project(token)
            >>> entries = project.get_list()
            >>> print(entries.json())
        """
        endpoint = '{}/osm/admin/v1/projects'.format(self.OSM_COMPONENTS.get('NBI-API'))
        headers = {"Authorization": "Bearer {}".format(self.bearer_token), "Accept": "application/json"}
        response = self.__client.get(endpoint, headers)
        return response

    def get(self, project_id=None):
        """Get details for a project in OSM r4 by given project ID

        Returns:
            obj: a requests object

        Examples:
            >>> from nbiapi.identity import bearer_token
            >>> from nbiapi.project import Project
            >>> from settings import OSM_ADMIN_CREDENTIALS
            >>> token = bearer_token(OSM_ADMIN_CREDENTIALS.get('username'), OSM_ADMIN_CREDENTIALS.get('username'))
            >>> project = Project(token)
            >>> entry = project.get("admin")
            >>> print(entry.json())
        """
        endpoint = '{}/osm/admin/v1/projects/{}'.format(self.OSM_COMPONENTS.get('NBI-API'), project_id)
        headers = {"Authorization": "Bearer {}".format(self.bearer_token), "Accept": "application/json"}
        response = self.__client.get(endpoint, headers)
        return response
