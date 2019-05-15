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

import json, yaml, subprocess, time, datetime
import httplib2 as httplib

class RuleFile(object):

    def __init__(self, serviceID, rules):
        self.serviceID = serviceID
        self.rules = rules

    def relaodConf(self):
        print ('reload....')

    def buildRule(self, rule):
        rule = 'ALERT ' + rule['name'].replace (" ", "_") +'\n'+'  IF ' + rule['condition'] + '\n'+'  FOR ' + rule['duration'] + '\n'+'  LABELS { serviceID = "' + self.serviceID +'" }'+'\n'+'  ANNOTATIONS { '+'\n'+'    summary = "Instance {{ $labels.instance }} down",'+'\n'+'    description = "{{ $labels.instance }} of job {{ $labels.job }} has been down for more than 5 minutes.",'+'\n'+'}'+'\n'
        return rule

    def writeFile(self):
        body = ''
        for r in self.rules:
            body += self.buildRule(r)
        filename = "".join(('/opt/Monitoring/prometheus-0.17.0rc2.linux-amd64/rules/',self.serviceID, '.rules'))

        with open(filename, 'w') as outfile:
            outfile.write(body)
        #    json.dump(body, outfile)

        if self.validate(filename) == 0:
            print ("RuleFile created SUCCESSFULLY")
            #add file to conf file
            with open('/opt/Monitoring/prometheus-0.17.0rc2.linux-amd64/prometheus.yml', 'r') as conf_file:
                conf = yaml.load(conf_file)
                for rf in conf['rule_files']:
                    if filename in rf:
                        return
                conf['rule_files'].append(filename)
                print (conf['rule_files'])
                with open('/opt/Monitoring/prometheus-0.17.0rc2.linux-amd64/prometheus.yml', 'w') as yml:
                    yaml.safe_dump(conf, yml)
                self.reloadServer()
                
            #reload conf

    def validate(self,file):
        p = subprocess.Popen(['/opt/Monitoring/manager/promtool', 'check-rules', file], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, status = p.communicate()
        print (status)
        rc = p.returncode
        if rc == 0:
            if 'SUCCESS' in status:
                return 0
            else:
                return 10
        else:
            return rc

    def reloadServer(self):
        httpServ = httplib.HTTPConnection("localhost", 9090)
        httpServ.connect()
        httpServ.request("POST", "/-/reload")
        response = httpServ.getresponse()
        print (response.status)
        httpServ.close()


class ProData(object):

    def __init__(self, srv_addr_, srv_port_):
        self.srv_addr = srv_addr_
        self.srv_port = srv_port_

    def getMetrics(self):
        now = int(datetime.datetime.utcnow().timestamp())
        path = "".join(("/api/v1/label/__name__/values?_=", str(now)))
        d = self.HttpGet(self.srv_addr,self.srv_port,path)
        return d

    def getMetricsResId(self,key,id,tm_window):
        now = int(datetime.datetime.utcnow().timestamp())
        path = "".join(("/api/v1/series?match[]={"+key+"=\""+id+"\"}&start=", str(now-500), "&end=",str(now)))
        if tm_window:
            tm_window = '['+tm_window+']'
        else:
            tm_window = ''
        d = self.HttpGet(self.srv_addr,self.srv_port,path)
        if key == 'container_name':
            pod_name = d['data'][0]['pod_name']
            print(pod_name)
            now = int(datetime.datetime.utcnow().timestamp())
            path = "".join(
                ("/api/v1/series?match[]={__name__=~\"^container_network.*\",container_name=\"POD\",pod_name=\"" + pod_name + "\"}&start=", str(now - 500), "&end=", str(now)))
            print(path)
            tf_mtr = self.HttpGet(self.srv_addr, self.srv_port, path)

        resp = []
        print (d['data'])
        for mt in d['data']:
            if mt['__name__'] == 'ALERTS' or mt['__name__'] == 'ALERTS_FOR_STATE':
                continue
            mt.pop('instance',None)
            mt.pop('id', None)
            mt.pop('group',None)
            mt.pop('job', None)
            if tm_window != '':
                dt = self.getMetricData(key,id, mt['__name__'],tm_window)
                mt['data'] = dt
            resp.append(mt)
        if key == 'container_name':
            for mt in tf_mtr['data']:
                mt.pop('instance', None)
                mt.pop('id', None)
                mt.pop('group', None)
                mt.pop('job', None)
                if tm_window != '':
                    dt = self.getMetricData('pod_name',pod_name, mt['__name__'],tm_window)
                    mt['data'] = dt
                resp.append(mt)
        print (len(resp))
        d['data'] = resp
        return d

    def getMetricData(self,key,vdu,metric_name,time_window):
        path = "".join(("/api/v1/query?query=", str(metric_name), "{"+key+"=\"" + vdu + "\"}"+time_window))
        d = self.HttpGet(self.srv_addr, self.srv_port, path)
        dt = []
        if 'status' in d:
            if 'data' in d:
                if 'result' in d['data'] and len(d['data']['result']) > 0:
                    if d['status'] == 'success':
                        if 'value' in d['data']['result'][0]:
                            dt = d['data']['result'][0]['value']
                        elif 'values' in d['data']['result'][0]:
                            dt = d['data']['result'][0]['values']
        return dt

    def getMetricFullDetail(self, metric_name):
        path = "".join(("/api/v1/query?query=", str(metric_name)))
        d = self.HttpGet(self.srv_addr,self.srv_port,path)
        return d

    def getMetricDetail(self,key, vdu, metric_name):
        path = "".join(("/api/v1/query?query=", str(metric_name), "{"+key+"=\""+vdu+"\"}"))
        d = self.HttpGet(self.srv_addr,self.srv_port,path)
        return d


    def getTimeRangeData(self, req):
        try:
            if len(req['labels']) == 0:
                path = "".join(("/api/v1/query_range?query=",req['name'],"&start=",req['start'],"&end=",req['end'],"&step=",req['step'] ))
            elif len(req['labels']) == 1:
                l='{'+req['labels'][0]['labeltag']+'="'+req['labels'][0]['labelid']+'"}'
                path = "".join(("/api/v1/query_range?query=",req['name'],l,"&start=",req['start'],"&end=",req['end'],"&step=",req['step'] ))
            else:
                ls = "{"
                for lb in req['labels']:
                    ls+=lb['labeltag']+'="'+lb['labelid']+'",'
                ls = ls[:-1]
                ls+='}'
                path = "".join(("/api/v1/query_range?query=",req['name'],ls,"&start=",req['start'],"&end=",req['end'],"&step=",req['step'] ))
        except KeyError:
            path = "".join(("/api/v1/query_range?query=",req['name'],"&start=",req['start'],"&end=",req['end'],"&step=",req['step'] ))
        print (path)
        d = self.HttpGet(self.srv_addr,self.srv_port,path)
        return d

    def getTimeRangeDataVnf(self, req):
        try:
            if len(req['labels']) == 0:
                path = "".join(("/api/v1/query_range?query=",req['name'],"&start=",req['start'],"&end=",req['end'],"&step=",req['step'] ))
            elif len(req['labels']) == 1:
                l='{'+req['labels'][0]['labeltag']+'="'+req['labels'][0]['labelid']+'"}'
                path = "".join(("/api/v1/query_range?query=",req['name'],l,"&start=",req['start'],"&end=",req['end'],"&step=",req['step'] ))
            else:
                ls = "{"
                for lb in req['labels']:
                    ls+=lb['labeltag']+'="'+lb['labelid']+'",'
                ls = ls[:-1]
                ls+='}'
                path = "".join(("/api/v1/query_range?query=",req['name'],ls,"&start=",req['start'],"&end=",req['end'],"&step=",req['step'] ))
        except KeyError:
            path = "".join(("/api/v1/query_range?query=",req['name'],"&start=",req['start'],"&end=",req['end'],"&step=",req['step'] ))
        print (path)
        d = self.HttpGet(self.srv_addr,self.srv_port,path)
        return d

    def HttpGet(self, srv_addr,srv_port,path):
        url = 'http://'+srv_addr+':'+str(srv_port)+''+path
        httpServ = httplib.Http()
        response = httpServ.request(url, method='GET')
        if response[0].status == 200:
            data = json.loads(response[1].decode())
        else:
            data = {'response_status':response[0].status}
        return data
