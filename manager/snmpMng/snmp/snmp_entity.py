## Copyright (c) 2015 SONATA-NFV, 2017 5GTANGO [, ANY ADDITIONAL AFFILIATION]
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

from snmp.planner import Scheduler
from snmp.prompw import Pusher

class Server(object):

    def __init__(self, ip_, port_, tm_int_, ent_type_, ent_id_,logger_, pw_srv_):
        self.version = 3
        self.auth_protocol = 'MD5'
        self.secutity_level = 'authnoPriv'
        self.creds = {}
        self.oids = {}
        self.ip = ip_
        self.port = port_
        self.interval = tm_int_
        self.entity_type = ent_type_
        self.entity_id = ent_id_
        self.servers = []
        for srv in pw_srv_:
            pusher = Pusher(pw_url_=srv, node_name_=''+ent_type_+':'+ent_id_, id_=ent_id_)
            self.servers.append(pusher)


    def credentials(self, username_, password_, auth_prot_, secur_lev_):
        self.creds['user'] = username_
        self.creds['pass'] = password_
        if auth_prot_:
            self.auth_protocol = auth_prot_

        if secur_lev_:
            self.secutity_level = secur_lev_


    def updateOID(self, oid_):
        if not oid_.id in self.oids:
            self.oids[oid_.id] = oid_

    def removeOID(self,oid_id_):
        if oid_id_ in self.oids:
            self.oids.pop(oid_id_)

    def updateVal(self,varBind_):
        #Check if its float
        oid = str(varBind_[0])#'1.3.6.1.4.1.8072.1.3.2.3.1.2.21.119.97.99.45.112.114.111.118.105.115.105.111.110.101.100.45.117.115.101.114.115'
        self.oids[oid].value = varBind_[1]
        for pusher in self.servers:
            pusher.sendGauge(metric=self.oids[oid].metric_name.replace('-','_'), description=self.oids[oid].description, value=self.oids[oid].value,
                                job='snmp', labels={'ip':self.ip,'port':self.port})
        return self.oids[oid]



class oid(object):

    def __init__(self, oid_, mtr_name_, unit_, mib_name_):
        self.id = oid_
        self.metric_name = mtr_name_
        self.type = 'gauge'
        self.description = '' + mib_name_ + ' ' + oid_
        self.unit = unit_
        self.name = mib_name_
        self.value = 0

if __name__ == '__main__':
    ent = Server('localhost',161,3,'vnf','123456789', None, None)
    ent.credentials('authOnlyUser', 'supercalifrajilistico','MD5','authnoPriv')
    oid1 = oid('1.3.6.1.4.1.8072.1.3.2.3.1.2.21.119.97.99.45.112.114.111.118.105.115.105.111.110.101.100.45.117.115.101.114.115',
              'wac-provisioned-users',
              'count',
              'NET-SNMP-EXTEND-MIB::nsExtendOutputFull')
    ent.updateOID(oid1)
    oid2 = oid('1.3.6.1.4.1.8072.1.3.2.3.1.2.17.119.97.99.45.114.101.103.105.115.116.114.97.116.105.111.110.115',
               'wac-registrations',
               'count',
               'NET-SNMP-EXTEND-MIB::nsExtendOutputFull')
    ent.updateOID(oid2)
    ent.removeOID('1.3.6.1.4.1.8072.1.3.2.3.1.2.21.119.97.99.45.112.114.111.118.105.115.105.111.110.101.100.45.117.115.101.114.115')
    print(ent.oids)

