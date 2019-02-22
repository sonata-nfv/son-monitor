## ALL RIGHTS RESERVED.
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
## Neither the name of the SONATA-NFV, 5GTANGO [, ANY ADDITIONAL AFFILIATION]
## nor the names of its contributors may be used to endorse or promote
## products derived from this software without specific prior written
## permission.
##
## This work has been performed in the framework of the SONATA project,
## funded by the European Commission under Grant number 671517 through
## the Horizon 2020 and 5G-PPP programmes. The authors would like to
## acknowledge the contributions of their colleagues of the SONATA
## partner consortium (www.sonata-nfv.eu).
##
## This work has been performed in the framework of the 5GTANGO project,
## funded by the European Commission under Grant number 761493 through
## the Horizon 2020 and 5G-PPP programmes. The authors would like to
## acknowledge the contributions of their colleagues of the 5GTANGO
## partner consortium (www.5gtango.eu).
# encoding: utf-8

import json, yaml, datetime, time
from django.db import IntegrityError
from django.db.models import Q
from api.models import monitoring_services
from api.models import monitoring_functions

class Osm(object):

    def __init__(self):
        self.mano_type = 'osm'
        pass


    def instatiate_NS(self, nsr):
        #check if NS exists
        ns_id = nsr['ns']['id']
        srv = monitoring_services.objects.all().filter(sonata_srv_id=ns_id)

        if srv.count() == 0:
            # Store new NS
            srv = monitoring_services(sonata_srv_id=ns_id, name=nsr['ns']['name'],
                                      description = self.mano_type+":"+nsr['ns']['nsd_id'])
            srv.save()
            srv_pk = srv.id
        else:
            srv_pk = srv.first().id

        func = monitoring_functions.objects.all().filter(Q(service__sonata_srv_id=ns_id) & Q(sonata_func_id=nsr['vnf']['id']))
        if func.count() > 0:
            func.delete()

        name = 'undefined'
        if nsr['vnf']['name']:
            name = nsr['vnf']['name']
        func = monitoring_functions(service_id=srv_pk, host_id=nsr['vdu']['id'],
                                        name=name,
                                        sonata_func_id=nsr['vnf']['id'],
                                        description="vnfd_id:"+nsr['vnf']['vnfd_id'],
                                        pop_id=nsr['vim']['uuid'])
        func.save()



    def terminate_NS(self,ns_id):
        srv = monitoring_services.objects.all().filter(sonata_srv_id=ns_id)
        srv.delete()