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


import logging, os, json,time
from logging.handlers import RotatingFileHandler
from Configure import Configuration
from snmp import snmp_entity
from sqlDB import psHandler
from logger import TangoLogger as TangoLogger

def init(logger):
    global prometh_server
    global job
    global workers
    global postgres_port
    global postgres_host
    global db_uname
    global db_upass

    workers = {}
    conf = Configuration("/opt/Monitoring/exporter.conf",logger)
    postgres_port = os.getenv('POSTGS_PORT', conf.ConfigSectionMap("sqlDB")['port'])
    postgres_host = os.getenv('POSTGS_HOST', conf.ConfigSectionMap("sqlDB")['host'])
    db_uname = os.getenv('DB_USER_NAME', conf.ConfigSectionMap("sqlDB")['user'])
    db_upass= os.getenv('DB_USER_PASS', conf.ConfigSectionMap("sqlDB")['pass'])
    prometh_server = os.getenv('PROM_SRV', conf.ConfigSectionMap("Prometheus")['server_url'])
    job = 'snmp_vnf'
    if is_json(prometh_server):
        prometh_server = json.loads(prometh_server)
    else:
        prometh_server = [prometh_server]



def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError:
    return False, None
  return True, json_object

def getEntities():
    h = psHandler.PShld(usr_=db_uname, psw_=db_upass, host_=postgres_host, port_=postgres_port)
    ents = h.getEntities('ACTIVE')
    if not ents:
        logger.info('No ACTIVE SNMP AGENTS FOUND')

    for ent in ents:
        e = snmp_entity.Server(ip_=ent.ip, port_=ent.port, tm_int_=ent.interval, ent_type_=ent.entity_type,
                               ent_id_=ent.entity_id, logger_=logger, pw_srv_=prometh_server, version_=ent.version)
        e.credentials(ent.username, ent.password, ent.auth_protocol, ent.security_level)
        for oid in ent.oids:
            o = snmp_entity.oid(oid.oid, oid.metric_name, oid.unit, oid.mib_name)
            e.updateOID(o)
        w = {}
        sh = snmp_entity.Scheduler(e,logger)
        sh.timer.start()
        workers[str(str(ent.id) + ":" + e.ip + ':' + e.port)] = sh
    h.session.close()

def updateEntities():
    h = psHandler.PShld(usr_=db_uname, psw_=db_upass, host_=postgres_host, port_=postgres_port)
    ents = h.getEntities('UPDATED')
    dl_ents = h.getEntities('DELETED')
    if not ents:
        logger.info('No UPDATED SNMP AGENTS FOUND')

    for ent in ents:
        lb = str(str(ent.id) + ":"+ ent.ip + ':' + ent.port)
        if lb in workers:
            workers[str(str(ent.id) + ":"+ ent.ip + ':' + ent.port)].stopThread()
            del workers[str(str(ent.id) + ":"+ ent.ip + ':' + ent.port)]
        e = snmp_entity.Server(ip_=ent.ip, port_=ent.port, tm_int_=ent.interval, ent_type_=ent.entity_type,
                               ent_id_=ent.entity_id, logger_=logger, pw_srv_=prometh_server,version_=ent.version)
        e.credentials(ent.username, ent.password, ent.auth_protocol, ent.security_level)
        for oid in ent.oids:
            o = snmp_entity.oid(oid.oid, oid.metric_name, oid.unit, oid.mib_name)
            e.updateOID(o)

        sh = snmp_entity.Scheduler(e,logger)
        sh.timer.start()
        workers[str(str(ent.id) + ':' + e.ip + ':' + e.port)] = sh
        h.updateEntStatus(host_=e.ip,port_=e.port,status_='ACTIVE')
        logger.info('SNMP ENTITY UPDATED '+ str(e.ip + ':' + e.port))

    for ent in dl_ents:
        lb = str(str(ent.id) + ":"+ ent.ip + ':' + ent.port)
        h.deleteEntity(id_=ent.id, host_=ent.ip, port_=ent.port)
        if lb in workers:
            workers[lb].stopThread()
            del workers[lb]
    h.session.close()


if __name__ == '__main__':
    logger = TangoLogger.getLogger(__name__, log_level=logging.INFO, log_json=True)
    TangoLogger.getLogger("SNMP_Manager", logging.INFO, log_json=True)
    logger.setLevel(logging.INFO)

    #logger = logging.getLogger('SNMP_Manager')
    #hdlr = RotatingFileHandler('snmp_manager.log', maxBytes=1000000, backupCount=1)
    #formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    #hdlr.setFormatter(formatter)
    #logger.addHandler(hdlr)
    #logger.setLevel(logging.WARNING)
    #logger.setLevel(logging.INFO)
    init(logger)

    logger.info('====================')
    logger.info('SNMP Manager')
    logger.info('Promth P/W Server ' + json.dumps(prometh_server))

    getEntities()

    while 1:
        time.sleep(5)
        updateEntities()

