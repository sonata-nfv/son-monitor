import requests, os, json
import urllib3
import logging.config
from ..settings import LOGGING

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def bearer_token(username, password):
    """Get bearer authorization token from OSM r4

    Args:
        username (str): The admin OSM r4 username
        password (str): The admin OSM r4 password

    Returns:
        token (str): An authorization token

    Examples:
        >>> from nbiapi.identity import bearer_token
        >>> from settings import OSM_COMPONENTS
        >>> token = bearer_token("admin", "admin")
        >>> assert type(token) is str
    """
    if not isinstance(username, str):
        raise TypeError("The given type of username is `{}`. Expected str.".format(type(username)))
    if not isinstance(password, str):
        raise TypeError("The given type of password is `{}`. Expected str.".format(type(password)))

    OSM_COMPONENTS = os.environ.get('OSM_COMPONENTS')
    if OSM_COMPONENTS is None:
        print('NO OSM_COMPONENTS in ENV')
        return

    OSM_COMPONENTS = json.loads(OSM_COMPONENTS)
    endpoint = '{}/osm/admin/v1/tokens'.format(OSM_COMPONENTS.get('NBI-API'))
    params = {'username': username, 'password': password}
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.post(url=endpoint, params=params, headers=headers, verify=False)
    logger.debug("Request `GET {}` returns HTTP status `{}`, headers `{}` and body `{}`."
                 .format(response.url, response.status_code, response.headers, response.text))
    if response.status_code == 200:
        return response.json()['id']
    return None
