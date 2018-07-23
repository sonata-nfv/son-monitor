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

import threading,sys,uuid,time
import datetime
from pysnmp.hlapi import *



class Scheduler(object):

    def __init__(self, snmp_entity_, logger_):
        self.snmp_server = snmp_entity_
        self.stop_thread = False
        self.logger = logger_
        self.uuid = uuid.uuid1()
        self.timer = threading.Thread(target=self.collectDt, args=(int(self.snmp_server.interval), lambda: self.stop_thread))
        self.timer.daemon = True
        self.logger.info('worker: ' + str(self.uuid) +' created')

    def getValues(self):
        oids = []
        for id in self.snmp_server.oids.keys():
            oids.append(ObjectType(ObjectIdentity(id)))

        if self.snmp_server.creds['user'] == 'public':
            ct = CommunityData('public')
        else:
            ct = UsmUserData(self.snmp_server.creds['user'], self.snmp_server.creds['pass'])

        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   ct,
                   UdpTransportTarget((self.snmp_server.ip, self.snmp_server.port)),
                   ContextData(),
                   *oids
                   ))

        if errorIndication:
            self.logger.error(errorIndication.prettyPrint())
            print(errorIndication)
        elif errorStatus:
            self.logger.error(errorStatus.prettyPrint())
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
            return varBinds

    def stopThread(self):
        self.stop_thread = True
        self.timer.join()

    def collectDt(self,interval_, stop_):
        lastclick = None

        while True:
            self.logger.info('============')
            nowclick = int(round(time.time() * 1000))
            if lastclick:
                self.logger.info('actual interval '+str(nowclick - lastclick))
            lastclick = nowclick

            try:
                varBinds = self.getValues()
                for varBind in varBinds:
                    self.logger.info('%s get values for entity %s %s metric: %s' % (self.uuid, self.snmp_server.ip, self.snmp_server.port, varBind[0]) )
                    oid = self.snmp_server.updateVal(varBind)
            except Exception as e:
                self.logger.exception(e)
                print(str(e))
            except:
                self.logger.error("General error on retrieving snmp oid: {0} ".format(sys.exc_info()[0]))
                print("General exception")
            if stop_():
                break
            time.sleep(interval_)

    def __del__(self):
        self.logger.info('worker: ' + str(self.uuid) + ' died')


class myTimer(threading.Thread):

    def __init__(self,t,hFunction):
        super(myTimer, self).__init__()
        self.t=t
        stopThread = False
        self.hFunction = hFunction
        self.thread = threading.Timer(self.t,self.handle_function, lambda: stopthread)
        self.stoprequest = threading.Event()


    def handle_function(self):
        self.hFunction()
        self.thread = threading.Timer(self.t,self.handle_function)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()


    def join(self, timeout=None):
        self.stoprequest.set()
        super(myTimer, self).join(timeout)


