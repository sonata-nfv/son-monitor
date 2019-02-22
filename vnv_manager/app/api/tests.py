'''
Copyright (c) 2015 SONATA-NFV [, ANY ADDITIONAL AFFILIATION]
ALL RIGHTS RESERVED.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Neither the name of the SONATA-NFV [, ANY ADDITIONAL AFFILIATION]
nor the names of its contributors may be used to endorse or promote 
products derived from this software without specific prior written 
permission.

This work has been performed in the framework of the SONATA project,
funded by the European Commission under Grant number 671517 through 
the Horizon 2020 and 5G-PPP programmes. The authors would like to 
acknowledge the contributions of their colleagues of the SONATA 
partner consortium (www.sonata-nfv.eu).
'''

from django.test import TestCase
from api.models import monitoring_users
import json, requests, os


# Create your tests here.

class UsersTestCase(TestCase):
    def setUp(self):
        monitoring_users.objects.create(first_name='fname', last_name='lname', email='example@email.com', type='dev',
                                        sonata_userid='1234567890')

    def test_user_email(self):
        usr = monitoring_users.objects.get(sonata_userid='1234567890')
        self.assertEqual(usr.email, 'example@email.com', "UserTestPass")


class ApisTestCase(TestCase):
    def test_users(self):
        response = self.client.get('/api/v1/users')
        self.assertEqual(response.status_code, 200)

    def test_metrics(self):
        response = self.client.get('/api/v1/metrics')
        self.assertEqual(response.status_code, 200)

    def test_services(self):
        response = self.client.get('/api/v1/services')
        self.assertEqual(response.status_code, 200)

    def test_functions(self):
        response = self.client.get('/api/v1/functions')
        self.assertEqual(response.status_code, 200)

    def test_notification_types(self):
        response = self.client.get('/api/v1/notification/types')
        self.assertEqual(response.status_code, 200)

    def test_policy_rules(self):
        response = self.client.get('/api/v1/policymng/rules')
        self.assertEqual(response.status_code, 200)

    def test_sla_rules(self):
        response = self.client.get('/api/v1/slamng/rules')
        self.assertEqual(response.status_code, 200)

    def test_snmp_entities(self):
        response = self.client.get('/api/v1/metrics')
        self.assertEqual(response.status_code, 200)


class IntTestCase(TestCase):

    def testPrometheusPW(self):
        # Check Prometheus Pushgateway server
        response = requests.get('http://pushgateway:9091/status')
        self.assertEqual(response.status_code, 200,'int.test.1: Pushgateway server FAILURE')

    def testPrometheusSvr(self):
        # Check Prometheus server
        response = requests.get('http://prometheus:9090/status')
        self.assertEqual(response.status_code, 200,'int.test.2: Prometheus server FAILURE')

    def testMonManagerSvr(self):
        # Check Monitoring Manager
        response = requests.get('http://manager:8000/pings')
        self.assertEqual(response.status_code, 200, 'int.test.2: Monitoring Mamager FAILURE')

    def testDBconnection(self):
        # Create User
        response = self.client.post('/api/v1/users',
                                    {"first_name": "John", "last_name": "Smith", "email": "user@email.com",
                                     "sonata_userid": "123456", "type": "cst"})
        usr_id = response.json()['id']
        self.assertEqual(response.status_code, 201, 'int.test.3: Monitoring Manager FAILURE')

        # Retrieve User
        response = self.client.get('/api/v1/user/' + str(usr_id) + '/')
        self.assertEqual(response.status_code, 200, 'int.test.3: Monitoring Manager FAILURE')

    def testPrometheusConf(self):
        # Retrieve Prometheus configuration
        response = self.client.get('/api/v1/prometheus/configuration')
        self.assertEqual(response.status_code, 200, 'int.test.4: Get Prometheus configuration FAILURE')

    def testPrometheusMetrics(self):
        # Retrieve avialable metrics on Prometheus server
        response = self.client.get('/api/v1/prometheus/metrics/list')
        self.assertEqual(response.status_code, 200, 'int.test.5: Get Prometheus metrics FAILURE')

    def testCreateNS(self):
        # Create Notifications
        response = self.client.post('/api/v1/notification/types',{"type": "rabbitmq"})
        self.assertEqual(response.status_code, 201, 'int.test.6.1: Create mock NS FAILURE')

        # Create NS
        TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'resources/new_service.json')
        with open(TESTDATA_FILENAME) as f:
            data = json.load(f)
        ns_id = data['service']['sonata_srv_id']
        response = self.client.post('/api/v1/service/new', json.dumps(data),content_type="application/json")
        self.assertEqual(response.status_code, 200, 'int.test.6.2: Create mock NS FAILURE')

        # GET NS
        response = self.client.get('/api/v1/service/'+ns_id+'/')
        self.assertEqual(response.status_code, 200, 'int.test.6.3: Create mock NS FAILURE')

        # GET SNMP ENTITIES
        response = self.client.get('/api/v1/snmp/entities')
        self.assertEqual(response.status_code, 200)
        count = response.json()['count']
        self.assertEqual(response.json()['count'],1,'int.test.6.4: SNMP entity NOT set')

    '''
    def testAlertNotification(self):
        #Define notification type
        response = self.client.post('/api/v1/notification/types',{"type": "rabbitmq"})
        self.assertEqual(response.status_code, 201)

        #Create a dummy NS
    
        srv = {"service":{"sonata_srv_id":"005606ed-be7d-4ce3-983c-847039e3a5a3","name":"sonata-mon-test","description":"The network service descriptor for the SONATA demo.","pop_id":"null","sonata_usr": {"phone": "null","email": "pkarkazis@synelixis.com"},"host_id":"null"},"functions":[{"sonata_func_id":"24f89c1a-1259-4a1f-b0fd-c3ae99a4b626","name":"firewall-vnf","description":"A first firewall VNF descriptor.","pop_id":"123","host_id":"0123456789","metrics":[{"name":"vm_cpu_perc_test","interval":"null","units":"Percentage","cmd":"null","description":"null","threshold":"null"}]}],"rules":[{"name":"mon:rule:vm_cpu_perc_test","duration":"2s","notification_type":2,"condition":"0123456789:vm_cpu_perc_test > 90","summary":"cpu-perc-test","description":"if cpu exceeds 90%"}]}
        response = self.client.post('/api/v1/service/new',
                                    {"service": {"sonata_srv_id": "005606ed-be7d-4ce3-983c-847039e3a5a3",
                                                 "name": "sonata-mon-test",
                                                 "description": "The network service descriptor for the SONATA demo.",
                                                 "pop_id": "null",
                                                 "sonata_usr": {"phone": "null", "email": "pkarkazis@synelixis.com"},
                                                 "host_id": "null"}, "functions": [
                                        {"sonata_func_id": "24f89c1a-1259-4a1f-b0fd-c3ae99a4b626",
                                         "name": "firewall-vnf", "description": "A first firewall VNF descriptor.",
                                         "pop_id": "123", "host_id": "0123456789", "metrics": [
                                            {"name": "vm_cpu_perc_test", "interval": "null", "units": "Percentage",
                                             "cmd": "null", "description": "null", "threshold": "null"}]}], "rules": [
                                        {"name": "mon:rule:vm_cpu_perc_test", "duration": "2s", "notification_type": 2,
                                         "condition": "0123456789:vm_cpu_perc_test > 90", "summary": "cpu-perc-test",
                                         "description": "if cpu exceeds 90%"}]}

                                    )
        self.assertEqual(response.status_code, 201)
'''
