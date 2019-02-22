import os,json
from .exceptions import NsValueIsNotDict, NsUuidDoesNotExist
from .nbiapi.identity import bearer_token
from .nbiapi.ns import Ns
from .nbiapi.vim import Vim
from .nbiapi.vnf import Vnf




def getToken():
    creds = os.environ.get('OSM_ADMIN_CREDENTIALS')
    token = None
    if creds:
        creds = json.loads(creds)
        token = bearer_token(str(creds.get('username')), str(creds.get('username')))
    return token


def get_ns_uuid_from_message(message):
    """Extract the UUID of the NS to be instantiated/terminated from the message

    In the OSM  r4, the message looks like as follows:
    --
    {
        "_admin": {
            "created": "1527159237.137106",
            "modified": "1527159237.137106"
        },
        "_id": "f850ebf3-a487-4fe6-bafa-6245c8b537e1",
        "id": "f850ebf3-a487-4fe6-bafa-6245c8b537e1",
        "isAutomaticInvocation": "false",
        "isCancelPending": "false",
        "lcmOperationType": "terminate",
        "links": {
            "nsInstance": "/osm/nslcm/v1/ns_instances/af6de0c1-7279-427e-9b68-1fa0e493d31d",
            "self": "/osm/nslcm/v1/ns_lcm_op_occs/f850ebf3-a487-4fe6-bafa-6245c8b537e1"
        },
        "nsInstanceId": "af6de0c1-7279-427e-9b68-1fa0e493d31d",
        "operationParams": {
            "_id": "f850ebf3-a487-4fe6-bafa-6245c8b537e1",
            "autoremove": "true",
            "nsInstanceId": "af6de0c1-7279-427e-9b68-1fa0e493d31d"
        },
        "operationState": "PROCESSING",
        "startTime": "1527159237.1370444",
        "statusEnteredTime": "1527159237.1370444"
    }
    --

    Args:
        message (dict): The value of the message as it was published in teh Kafka broker

    Returns:
        str: The UUID of the NS to be instantiated/terminated
    """
    if not isinstance(message, dict):
        raise NsValueIsNotDict('The value of the message in the ns topic is not dict'.format(message))
    if 'nsInstanceId' not in message:
        raise NsUuidDoesNotExist(
            'The nsInstanceId key is not included in the value of the message {} in the topic ns'.format(message))
    return str(message['nsInstanceId'])


def convert_byte_to_str(term):
    """Convert a term from the bytes to str

    Args:
        term (bytes): The term in bytes

    Returns:
        str: The term in str
    """
    return term.decode("utf-8")


def compose_redis_key(vim_name, vdu_uuid):
    """Compose the key for redis given vim name and vdu uuid

    Args:
        vim_name (str): The VIM name
        vdu_uuid (str): The VDU uuid (NFVI based)

    Returns:
        str: the key for redis
    """
    return "{}:{}".format(vim_name.lower(), vdu_uuid)


def get_vim_info(vim_uuid=None):
    """Get the VIM name, type, url by given VIM uuid

    Args:
        vim_uuid (str): The VIM uuid

    Returns:
        dict: the VIM uuid, name, type and url
    """
    if vim_uuid is None:
        return {"uuid": vim_uuid, "name": None, "type": None, "url": None}

    creds = os.environ.get('OSM_ADMIN_CREDENTIALS')
    token = None
    if creds:
        creds = json.loads(creds)
        token = bearer_token(str(creds.get('username')), str(creds.get('username')))

    vim = Vim(token)
    response = vim.get(vim_uuid=vim_uuid)
    data = response.json()
    vim_info = {
        "uuid": vim_uuid,
        "name": data.get('name', None),
        "type": data.get('vim_type', None),
        "url": data.get('vim_url', None)
    }
    return vim_info


def get_vdus_info(ns_uuid=None):
    """Get information about NS, VNF(s) and VDU(s) by given NS uuid

    Args:
        ns_uuid (str): The NS uuid

    Returns:
        dict: ns, vnf and vdu info
    """
    vdus_info = []
    if ns_uuid is None:
        return vdus_info

    token = getToken()
    if token is None:
        return vdus_info

    ns = Ns(token)
    ns_response = ns.get(ns_uuid=ns_uuid)
    nsr = ns_response.json()

    # Get Vim
    vim_uuid = nsr.get('datacenter', None)
    vim_info = get_vim_info(vim_uuid=vim_uuid)

    # Get the Vnf UUIDs, members of the NS
    vnf_uuids = nsr.get('constituent-vnfr-ref', [])

    vnfr = Vnf(token)

    for vnf_uuid in vnf_uuids:
        vnf_response = vnfr.get(vnf_uuid=vnf_uuid)
        vnf_record = vnf_response.json()

        # VDUs info
        vdu_records = vnf_record.get('vdur', [])

        for vdu_record in vdu_records:
            mano = {
                "vim": vim_info,
                "ns": {
                    "id": ns_uuid,
                    "name": nsr.get('name-ref', None),
                    "nsd_id": nsr.get('nsdId', None),
                    "nsd_name": nsr.get('nsd-name-ref', None)
                },
                "vnf": {
                    "id": vnf_record.get("id", None),
                    "name": None, # not provided in osm r4
                    "short_name": None, # not provided in osm r4
                    "vnfd_id": vnf_record.get("vnfd-id", None),
                    "vnfd_name": None # not provided in osm r4
                },
                "vdu": {
                    "id": vdu_record.get("vim-id", None),  # NFVI-based uuid
                    "image_id": None,
                    "flavor": {},
                    "status": vdu_record.get("status", None),
                    "ip_address": vdu_record.get("ip-address", None),
                    "mgmt-interface": None  # future usage
                }
            }
            vdus_info.append(mano)
    return vdus_info
