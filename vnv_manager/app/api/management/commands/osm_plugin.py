import logging, os
import yaml,json
from django.core.management import BaseCommand
from kafka import KafkaConsumer
from api.management.commands.osm.utils import convert_byte_to_str, get_vdus_info, compose_redis_key
from .osm import osm
from api.management.commands.osm.exceptions import NsValueIsNotDict, NsUuidDoesNotExist


logger = logging.getLogger(__name__)


def osm_notification_handler():
    # See more: https://kafka-python.readthedocs.io/en/master/apidoc/KafkaConsumer.html
    kfk_cfg = os.environ.get('KAFKA_SETTINGS')
    if kfk_cfg is None:
        print('NO KAFKA_SETTINGS IN ENV')
        return
    kfk_obj = json.loads(kfk_cfg)
    consumer = KafkaConsumer(bootstrap_servers=kfk_obj['KAFKA_SERVER'], client_id=kfk_obj['KAFKA_CLIENT_ID'], enable_auto_commit=True,
                             value_deserializer=lambda v: yaml.safe_load(v.decode('utf-8', 'ignore')),
                             api_version=tuple(kfk_obj['KAFKA_API_VERSION']), )
    consumer.subscribe(kfk_obj['KAFKA_NS_MANAGER_TOPIC'])

    # Run each message in "ns" topic
    for message in consumer:
        logger.info(message)
        message_key = convert_byte_to_str(message.key)
        message_value = message.value

        if message_key == "instantiate":
            """
            An indicative sample of message is available in the file `samples/instantiate.json`.
            Since the NS instantiation is still in progress, we skip this info.
            """
            print("NS Creation in PROGRESS ")
            pass

        elif message_key == "instantiated":
            """
            When a new Network Service has successfully instantiated through OSM, a new entry is added in the Redis.
            The Redis is used as a cache to avoid continuous requests in OSM-r4 NBI API in the translation process.

            The translator could check if there is info in the redis related to the metric that is under process.
            If there is (`hit` case), then no call in OSM r4 NBI API is needed. In `miss` case, the OSM will be used. 

            The key is a composition of <vim_name>:<vdu_uuid>. Use lower function in `vim_name`.
            An indicative sample of message is available in the file `samples/instantiated.json`.
            """
            # Get the operational state of the process
            ns_operation_state = message_value['operationState']
            if ns_operation_state != 'COMPLETED':
                continue
            ns_uuid = message_value.get('nsr_id', None)
            print("NS Creation COMPLETED: "+ns_uuid)

            # Find the vdus for the new Network Service
            vdu_records = get_vdus_info(ns_uuid=ns_uuid)
            # Update the entries in the redis, if needed
            for vdu_record in vdu_records:
                vim_name = vdu_record.get("vim", {}).get('name', None)
                #print(vdu_record)
                if vim_name is None:
                    continue

                vdu_uuid = vdu_record.get("vdu", {}).get('id', None)
                if vdu_uuid is None:
                    continue

                osm.Osm().instatiate_NS(vdu_record)

        elif message_key == "terminate":
            """
            In this step, the NS termination is still in progress. However, this the proper time to remove the entries
            from redis since we can retrieve the vim information, since we can invoke the ns-instance web service. 

            An indicative sample of message is available in the file `samples/terminate.json`
            """
            ns_uuid = message_value.get('nsInstanceId', None)
            if ns_uuid is None:
                continue

            print("Termination in progress:"+ns_uuid)


        elif message_key == "terminated":
            """           
            When a new Network Service is terminated through OSM, delete the data from `InfluxDB` and the Redis. 
            The key is a composition of <vim_name>:<vdu_uuid>.

            An indicative sample of message is available in the file `samples/terminated.json`
            """
            # Get the operational state of the process
            ns_operation_state = message_value['operationState']
            if ns_operation_state != 'COMPLETED':
                continue
            ns_uuid = message_value.get('nsr_id', None)
            if ns_uuid is None:
                continue
            print("Termination completed:" + ns_uuid)
            osm.Osm().terminate_NS(ns_uuid)
        elif message_key == "action":
            "Future usage"
            pass
        elif message_key == "show":
            "Future usage"
            pass
        elif message_key == "deleted":
            "Future usage"
            pass


class Command(BaseCommand):
    def handle(self, *args, **options):
        '''
        # =================================
        # KAFKA SETTINGS
        # =================================
        kfk_cnf = {'KAFKA_SERVER':'192.168.1.172:9094', 'KAFKA_CLIENT_ID' : 'ns-manager',
                      'KAFKA_API_VERSION':(0, 10, 1), 'KAFKA_TOPICS':'ns'}

        # =================================
        # OSM SETTINGS
        # =================================
        OSM_IP = "192.168.1.172"  # "217.172.11.175"
        OSM_ADMIN_CREDENTIALS = {"username": "admin", "password": "admin"}
        osm_cnf = {'OSM_ADMIN_CREDENTIALS':{'username': 'admin', 'password': 'admin'}, 'OSM_COMPONENTS' : {'UI': 'http://{}:80'.format(OSM_IP),
                          'NBI-API': 'https://{}:9999'.format(OSM_IP),
                          'RO-API': 'http://{}:9090'.format(OSM_IP)}}
        '''

        osm_notification_handler()
'''
        vdu_record = [{'vnf': {'vnfd_id': '16c40d2e-7a1b-4f22-9e50-3f7ede3e9fc4',
                                   'id': 'b5921c88-906d-4bfb-9cf9-9cdfc98f93f0', 'vnfd_name': None, 'short_name': None,
                                   'name': None},
                           'vim': {'uuid': '30252cec-0ca4-493a-9321-b849f950869f',
                                   'url': 'http://192.168.1.147/identity/v3',
                                   'name': 'devstack-test', 'type': 'openstack'},
                           'ns': {'id': 'd6367403-05fe-4b98-9171-5a48375ed7a2', 'nsd_name': 'cirros_2vnf_ns',
                                  'name': 'test1',
                                  'nsd_id': 'd5c99561-ec46-4480-8377-b5b218b8b1e5'},
                           'vdu': {'id': '359da13e-ef4e-4203-9bd6-854cdfee5169', 'ip_address': '192.168.232.7',
                                   'image_id': None, 'mgmt-interface': None, 'flavor': {}, 'status': 'ACTIVE'}}, {
                              'vnf': {'vnfd_id': '16c40d2e-7a1b-4f22-9e50-3f7ede3e9fc4',
                                      'id': '74477fea-e149-458f-8a63-affbdb38443a', 'vnfd_name': None,
                                      'short_name': None,
                                      'name': None},
                              'vim': {'uuid': '30252cec-0ca4-493a-9321-b849f950869f',
                                      'url': 'http://192.168.1.147/identity/v3',
                                      'name': 'devstack-test', 'type': 'openstack'},
                              'ns': {'id': 'd6367403-05fe-4b98-9171-5a48375ed7a2', 'nsd_name': 'cirros_2vnf_ns',
                                     'name': 'test1', 'nsd_id': 'd5c99561-ec46-4480-8377-b5b218b8b1e5'},
                              'vdu': {'id': '47a7aa5b-fce1-4be5-b077-053882921477', 'ip_address': '192.168.232.10',
                                      'image_id': None, 'mgmt-interface': None, 'flavor': {}, 'status': 'ACTIVE'}}]
        osm.Osm().instatiate_NS(vdu_record[0])
        osm.Osm().instatiate_NS(vdu_record[1])
'''