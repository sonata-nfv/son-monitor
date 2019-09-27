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


import json, yaml, httplib2, subprocess, time, os
from shutil import copyfile

class fileBuilder(object):


    def __init__(self, file_name, cnfg, path):
        self.file_name = file_name
        self.configuration = cnfg
        self.prometheusPth = path
        self.PROM_VER = 2.4

    def relaodConf(self):
        print ('reload....')

    def buildYamlRulefl(self,rules,filename):
        obj = {'groups':[{'name':filename,'rules':[]}]}
        for r in rules:
            labels = ''
            print(r['labels'])
            r['name'] = r['name'].replace(':', '_')
            lbs = str(r['labels']).replace("'","").replace("[","").replace("]","").split(',')
            l = {}
            for lb in lbs:
                t=lb.split("=")
                l[str(t[0]).strip(" ")] = t[1].strip('/"')
            l['value'] = '{{ $value }}'
            rule = {'alert':r['name'],
                     'expr':self.conditionRule(r['condition']).strip('/"'),
                     'for':r['duration'],
                     'labels': l,
                     'annotations': {'summary': str(r['description'])}
                     }
            obj['groups'][0]['rules'].append(rule)
        return yaml.safe_dump(obj)

    def buildRule(self, rule):
        labels =''
        rule['name'] = rule['name'].replace(':','_')
        for lb in rule['labels']:
            labels += lb +', '        
        rule = 'ALERT ' + rule['name'].replace (" ", "_") +'\n'+'  IF ' + self.conditionRule(rule['condition']) + '\n'+'  FOR ' + rule['duration'] + '\n'+' LABELS {'+labels[:-2]+'}'+'\n'+'  ANNOTATIONS { '+'\n'+'    summary = "'+rule['summary']+' {{$labels.instance}}",'+'\n'+'    description = "'+rule['description']+' {{ $labels.instance }} of job {{ $labels.job }}",'+'\n'+'}'+'\n'
        return rule

    def conditionRule(self, rule):
        els = rule.split(" ")
        index = 0
        for el in els:
            if ':' in el:
                ep = el.split(':')
                els[index] = " "+ep[1]+'{resource_id=\"'+ep[0]+'\"} '
            index +=1
        return ''.join(str(x) for x in els)

    def writeFile(self):
        body = ''
        if self.PROM_VER == 0.17:
            for r in self.configuration:
                body += self.buildRule(r)
        else:
            body = self.buildYamlRulefl(self.configuration,self.file_name)

        filename = "".join((self.prometheusPth,'rules/',self.file_name, '.rules'))

        with open(filename, 'w') as outfile:
            outfile.write(body)
        #    json.dump(body, outfile)

        if self.validate(filename) == 0:
            #print "RuleFile created SUCCESSFULY"
            #add file to conf file
            with open(self.prometheusPth+'prometheus.yml', 'r') as conf_file:
                conf = yaml.load(conf_file)
                if conf['rule_files'] is None:
                    conf['rule_files'] = []
                for rf in conf['rule_files']:
                    if filename in rf:
                        self.reloadServer()
                        return "RuleFile updated SUCCESSFULY - SERVER Reloaded"
                conf['rule_files'].append(filename)
                print (conf['rule_files'])
                with open(self.prometheusPth+'prometheus.yml', 'w') as yml:
                    yaml.safe_dump(conf, yml)
                self.reloadServer()
            return "RuleFile created SUCCESSFULY - SERVER Reloaded"
        else:
            return "RuleFile creation FAILED"
        
    def validate(self,file):
        checktool = ''+self.prometheusPth+'promtool'
        p = subprocess.Popen([checktool,'check','rules',file], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, status = p.communicate()
        print (output)
        rc = p.returncode
        if rc == 0:
            if 'SUCCESS' in str(output):
                return 0
            else:
                return 10
        else:
            return rc

    def buildConf(self):
        resp={}
        self.file_name = self.prometheusPth+self.file_name
        with open(self.file_name+'.tmp', 'w') as yaml_file:
            yaml.safe_dump(self.configuration, yaml_file, default_flow_style=False)
        rs = self.validateConfig(self.file_name+'.tmp')
        if rs['code'] != 0:
            resp['report'] = str(rs['message'])
            resp['status'] = 'FAILED'
            resp['prom_reboot'] = None
        else:
            resp['report'] = "OK"
            if os.path.exists(self.file_name):
                copyfile(self.file_name, self.file_name+'.backup')
            if os.path.exists(self.file_name+'.tmp'):
                copyfile(self.file_name+'.tmp', self.file_name)
                resp['prom_reboot'] = self.reloadServer()
                if resp['prom_reboot'] == 'SUCCESS':
                    resp['status'] = 'SUCCESS'
        return resp

    def validateConfig(self,file):
        p = subprocess.Popen(['./promtool', 'check','config', file], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, status = p.communicate()
        rc = p.returncode
        msg={}
        msg['code'] = int(rc)
        msg['message'] =  status
        return msg


    def reloadServer(self):
        httpServ = httplib2.Http()
        try:
            url='http://127.0.0.1:9090/-/reload'
            response, content = httpServ.request(url,"POST")
            print (response.status)
            return 'SUCCESS'
        except Exception as e:
            print(str(e))
            return 'FAILED'

