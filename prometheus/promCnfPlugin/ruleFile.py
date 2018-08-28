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


import json, yaml, httplib, subprocess, time, os
from shutil import copyfile

class fileBuilder(object):

    def __init__(self, file_name, cnfg, path):
        self.file_name = file_name
        self.configuration = cnfg
        self.prometheusPth = path

    def relaodConf(self):
        print 'reload....'

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
                els[index] = " "+ep[1]+'{id=\"'+ep[0]+'\"} '
            index +=1
        return ''.join(str(x) for x in els)

    def writeFile(self):
        body = ''
        for r in self.configuration:
            body += self.buildRule(r)
        filename = "".join((self.prometheusPth,'rules/',self.file_name, '.rules'))

        with open(filename, 'w') as outfile:
            outfile.write(body)
        #    json.dump(body, outfile)

        if self.validate(filename) == 0:
            #print "RuleFile created SUCCESSFULY"
            #add file to conf file
            with open(self.prometheusPth+'prometheus.yml', 'r') as conf_file:
                conf = yaml.load(conf_file)
                for rf in conf['rule_files']:
                    if filename in rf:
                        self.reloadServer()
                        return "RuleFile updated SUCCESSFULY - SERVER Reloaded"
                conf['rule_files'].append(filename)
                print conf['rule_files']
                with open(self.prometheusPth+'prometheus.yml', 'w') as yml:
                    yaml.safe_dump(conf, yml)
                self.reloadServer()
            return "RuleFile created SUCCESSFULY - SERVER Reloaded"
        else:
            return "RuleFile creation FAILED"
        
    def validate(self,file):
        checktool = '.'+self.prometheusPth+'promtool'
        p = subprocess.Popen([checktool, 'check-rules', file], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, status = p.communicate()
        print status
        rc = p.returncode
        if rc == 0:
            if 'SUCCESS' in status:
                return 0
            else:
                return 10
        else:
            return rc

    def buildConf(self):
        resp={}
        with open(self.file_name+'.tmp', 'w') as yaml_file:
            yaml.safe_dump(self.configuration, yaml_file, default_flow_style=False)
        rs = self.validateConfig(self.file_name+'.tmp')
        resp['report']=rs['message']
        resp['status'] = 'FAILED'
        resp['prom_reboot'] = None
        if rs['status'] == 'SUCCESS':
            if os.path.exists(self.file_name):
                copyfile(self.file_name, self.file_name+'.backup')
            if os.path.exists(self.file_name+'.tmp'):
                copyfile(self.file_name+'.tmp', self.file_name)
                resp['prom_reboot'] = self.reloadServer()
                if resp['prom_reboot'] == 'SUCCESS':
                    resp['status'] = 'SUCCESS'
        return resp

    def validateConfig(self,file):
        p = subprocess.Popen(['./promtool', 'check-config', file], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, status = p.communicate()
        rc = p.returncode
        msg={}
        msg['code'] = rc
        msg['message'] =  status
        if not 'FAILED' in status:              
            msg['status'] = 'SUCCESS'
        else:
            msg['status'] = 'FAILED'
        return msg


    def reloadServer(self):
        httpServ = httplib.HTTPConnection("localhost", 9090)
        try:
            httpServ.connect()
            httpServ.request("POST", "/-/reload")
            response = httpServ.getresponse()
            print response.status
            httpServ.close()
            return 'SUCCESS'
        except:
            return 'FAILED'

