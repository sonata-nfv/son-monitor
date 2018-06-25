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
from api.views import SntServiceList


# Create your tests here.

class UsersTestCase(TestCase):
    def setUp(self):
        monitoring_users.objects.create(first_name='fname',last_name='lname',email='example@email.com',type='dev',sonata_userid='1234567890')

    def test_user_email(self):
        usr = monitoring_users.objects.get(sonata_userid='1234567890')
        self.assertEqual(usr.email,'example@email.com',"UserTestPass")

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
