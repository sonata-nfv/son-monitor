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

from sqlalchemy import create_engine, Table, Column, String, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql://monitoringuser:sonata@postgsql:5433/monitoring')
base = declarative_base()
class snmp_entities(base):
    __tablename__ = 'monitoring_snmp_entities'
    id = Column(String, primary_key=True)
    ip = Column(String)
    port = Column(String)
    interval = Column(String)
    entity_type = Column(String)
    entity_id = Column(String)
    version = Column(String)
    auth_protocol = Column(String)
    security_level = Column(String)
    status = Column(String)
    username = Column(String)
    password = Column(String)
    created = Column(String)

class snmp_oids(base):
    __tablename__ = 'monitoring_snmp_oids'
    id = Column(String, primary_key=True)
    snmp_entity_id = Column(String)
    oid  = Column(String)
    metric_name  = Column(String)
    metric_type  = Column(String)
    unit = Column(String)
    mib_name  = Column(String)
    created  = Column(String)


class PShld():

    def __init__(self,usr_,psw_,host_,port_):
        engine = create_engine('postgresql://'+usr_+':'+psw_+'@'+host_+':'+str(port_)+'/monitoring')
        base = declarative_base()
        Session = sessionmaker(engine)
        self.session = Session()


    def getEntities(self,status_):
        l = []
        entities = self.session.query(snmp_entities).filter_by(status=status_)
        for ent in entities:
            oids = self.session.query(snmp_oids).filter_by(snmp_entity_id=ent.id)
            if oids.count() == 0:
                continue
            e = ent
            e.oids = oids
            l.append(e)
        return l

    def updateEntStatus(self,host_,port_,status_):
        entities = self.session.query(snmp_entities).filter_by(ip=host_, port=port_)
        for ent in entities:
            ent.status = status_
            print (ent.ip, ent.port, ent.status)
        self.session.commit()

    def deleteEntity(self,host_,port_):
        entity = self.session.query(snmp_entities).filter_by(ip=host_, port=port_)
        oid = self.session.query(snmp_oids).filter_by(snmp_entity_id=entity[0].id).delete(synchronize_session=False)
        entity.delete(synchronize_session=False)
        self.session.commit()

if __name__ == '__main__':
    h = PShld(usr_='monitoringuser',psw_='sonata',host_='localhost',port_=5433)
    #h.getEntities('UPDATED')
    h.updateEntStatus('192.168.1.127','163','ACTIVE')
