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


from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import *
from api.serializers import *
from api.prometheus import *
#from api.serializers import UserSerializer
from django.http import Http404
from rest_framework import mixins
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework import permissions
from api.permissions import IsOwnerOrReadOnly
from rest_framework.reverse import reverse
from itertools import *
from django.forms.models import model_to_dict
import json, socket, os, base64
from drf_multiple_model.views import MultipleModelAPIView
from httpClient import Http
from django.db.models import Q
import datetime, psutil
from time import timezone
from django.db import IntegrityError



# Create your views here.


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'user': reverse('UserDetail', request=request, format=format),
        'tests': reverse('TestList', request=request, format=format),
        'test': reverse('TestDetail', request=request, format=format),
        'tests': reverse('UserList', request=request, format=format),
    })
########################################################################################

class SntPLCRuleconf(generics.CreateAPIView):
    serializer_class = SntPLCRulesConfSerializer

    def post(self, request, *args, **kwargs):
        srvid = self.kwargs['srvID']
        dt = request.data
        print(dt.keys())
        if 'plc_cnt' in dt.keys():
            policy_cnt = dt['plc_cnt']
        if 'vnfs' in dt.keys():
            vnfs = dt['vnfs']
        else:
            return Response({'error': 'Undefined vnfs'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if service exists
        srv = monitoring_services.objects.all().filter(sonata_srv_id=srvid)
        if srv.count() == 0:
            if srvid != 'generic':
                return Response({'error': 'Requested Service not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                srvid = 'alerts'


        # Delete old rule from DB
        rules_db = monitoring_rules.objects.all().filter(service__sonata_srv_id=srvid,consumer='PLC')
        rules_db.delete()

        # Create prometheus configuration file
        rls = {}
        rls['rules'] = []
        srvrules = []
        rules_status = 0
        rls['service'] = 'plc-'+srvid
        for vnf in dt['vnfs']:
            rls['vnf'] = vnf['nvfid']
            if 'vdus' in vnf.keys():
                for vdu in vnf['vdus']:
                    rls['vdu_id'] = vdu['vdu_id']
                    rules = vdu['rules']
                    rules_status += len(rules)
                    for r in rules:
                        print 'vnf '+ rls['vnf'] + ' vdu: '+ rls['vdu_id'] +json.dumps(r)
                        nt = monitoring_notif_types.objects.all().filter(id=r['notification_type']['id'])
                        if nt.count() == 0:
                            return Response({'error': 'Alert notification type does not supported. Action Aborted'},
                                status=status.HTTP_400_BAD_REQUEST)
                        else:
                            if srvid != "alerts":
                                print(rls['vnf'], rls['vdu_id'])
                                rule = monitoring_rules(service=srv[0], summary=r['summary'], notification_type=nt[0],
                                                    name=r['name'], condition=r['condition'], duration=r['duration'],
                                                    description=r['description'],consumer='PLC',function=rls['vnf'],vdu=rls['vdu_id'])
                                rule.save()
                        rl = {}
                        rl['name'] = r['name']
                        rl['description'] = r['description']
                        rl['summary'] = r['summary']
                        rl['duration'] = r['duration']
                        rl['notification_type'] = r['notification_type']
                        rl['condition'] = r['condition']
                        rl['labels'] = ["serviceID=\"" + srvid + "\", functionID=\""+rls['vnf']+"\", tp=\"PLC\""]
                        rls['rules'].append(rl)
                    srvrules += rules

        if len(srvrules) > 0:
            cl = Http()
            rsp = cl.POST('http://prometheus:9089/prometheus/rules', [], json.dumps(rls))
            if rsp == 200:
                return Response({'status': "success", "rules": rules_status})
            else:
                return Response({'error': 'Rule update fail ' + str(rsp)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'No rules defined'})

class SntPLCRulesDetail(generics.DestroyAPIView):
    serializer_class = SntRulesSerializer

    def delete(self, request, *args, **kwargs):
        queryset = monitoring_rules.objects.all()
        srvid = self.kwargs['sonata_srv_id']
        fq = queryset.filter(service__sonata_srv_id=srvid, consumer='PLC')

        if fq.count() > 0:
            fq.delete()
            cl = Http()
            rsp = cl.DELETE('http://prometheus:9089/prometheus/rules/' + str('plc-'+srvid), [])
            return Response({'staus': "service's rules removed"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'status': "rules not found"}, status=status.HTTP_404_NOT_FOUND)

class SntPLCRulesPerServiceList(generics.ListAPIView):
    serializer_class = SntRulesPerSrvSerializer

    def get_queryset(self):
        queryset = monitoring_rules.objects.all()
        srvid = self.kwargs['srvID']
        return queryset.filter(service__sonata_srv_id=srvid, consumer='PLC')

class SntPLCRulesList(generics.ListAPIView):
    serializer_class = SntRulesSerializer
    def get_queryset(self):
        queryset = monitoring_rules.objects.all()
        return queryset.filter(consumer='PLC')

class SntSLARuleconf(generics.CreateAPIView):
    serializer_class = SntSLARulesConfSerializer

    def post(self, request, *args, **kwargs):
        srvid = self.kwargs['srvID']
        dt = request.data
        print(dt.keys())
        if 'plc_cnt' in dt.keys():
            policy_cnt = dt['plc_cnt']
        if 'vnfs' in dt.keys():
            vnfs = dt['vnfs']
        else:
            return Response({'error': 'Undefined vnfs'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if service exists
        srv = monitoring_services.objects.all().filter(sonata_srv_id=srvid)
        if srv.count() == 0:
            if srvid != 'generic':
                return Response({'error': 'Requested Service not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                srvid = 'alerts'


        # Delete old rule from DB
        rules_db = monitoring_rules.objects.all().filter(service__sonata_srv_id=srvid, consumer='SLA')
        rules_db.delete()

        # Create prometheus configuration file
        rls = {}
        rls['rules'] = []
        srvrules = []
        rules_status = 0
        rls['service'] = 'sla-'+srvid
        for vnf in dt['vnfs']:
            rls['vnf'] = vnf['nvfid']
            if 'vdus' in vnf.keys():
                for vdu in vnf['vdus']:
                    rls['vdu_id'] = vdu['vdu_id']
                    rules = vdu['rules']
                    rules_status += len(rules)
                    for r in rules:
                        print 'vnf '+ rls['vnf'] + ' vdu: '+ rls['vdu_id'] +json.dumps(r)
                        nt = monitoring_notif_types.objects.all().filter(id=r['notification_type']['id'])
                        if nt.count() == 0:
                            return Response({'error': 'Alert notification type does not supported. Action Aborted'},
                                status=status.HTTP_400_BAD_REQUEST)
                        else:
                            if srvid != "alerts":
                                print(rls['vnf'], rls['vdu_id'])
                                rule = monitoring_rules(service=srv[0], summary=r['summary'], notification_type=nt[0],
                                                    name=r['name'], condition=r['condition'], duration=r['duration'],
                                                    description=r['description'],consumer='SLA',function=rls['vnf'],vdu=rls['vdu_id'])
                                rule.save()
                        rl = {}
                        rl['name'] = r['name']
                        rl['description'] = r['description']
                        rl['summary'] = r['summary']
                        rl['duration'] = r['duration']
                        rl['notification_type'] = r['notification_type']
                        rl['condition'] = r['condition']
                        rl['labels'] = ["serviceID=\"" + srvid + "\", functionID=\""+rls['vnf']+"\", tp=\"SLA\""]
                        rls['rules'].append(rl)
                    srvrules += rules

        if len(srvrules) > 0:
            cl = Http()
            rsp = cl.POST('http://prometheus:9089/prometheus/rules', [], json.dumps(rls))
            if rsp == 200:
                return Response({'status': "success", "rules": rules_status})
            else:
                return Response({'error': 'Rules update fail ' + str(rsp)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'No rules defined'})

class SntSLARulesDetail(generics.DestroyAPIView):
    serializer_class = SntRulesSerializer

    def delete(self, request, *args, **kwargs):
        queryset = monitoring_rules.objects.all()
        srvid = self.kwargs['sonata_srv_id']
        fq = queryset.filter(service__sonata_srv_id=srvid,consumer='SLA')

        if fq.count() > 0:
            fq.delete()
            cl = Http()
            rsp = cl.DELETE('http://prometheus:9089/prometheus/rules/' + str('sla-'+srvid), [])
            return Response({'status': "service's rules removed"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'status': "rules not found"}, status=status.HTTP_404_NOT_FOUND)

class SntSLARulesPerServiceList(generics.ListAPIView):
    serializer_class = SntRulesPerSrvSerializer

    def get_queryset(self):
        queryset = monitoring_rules.objects.all()
        srvid = self.kwargs['srvID']
        return queryset.filter(service__sonata_srv_id=srvid, consumer='SLA')

class SntSLARulesList(generics.ListAPIView):
    serializer_class = SntRulesSerializer
    def get_queryset(self):
        queryset = monitoring_rules.objects.all()
        return queryset.filter(consumer='SLA')


class SntSNMPEntCreate(generics.CreateAPIView):
    queryset = monitoring_snmp_entities.objects.all()
    serializer_class = SntSNMPEntFullSerializer

class SntSNMPEntList(generics.ListAPIView):
    queryset = monitoring_snmp_entities.objects.all()
    serializer_class = SntSNMPEntSerializer

class SntSNMPEntDetail(generics.DestroyAPIView):
    #queryset = monitoring_snmp_entities.objects.all()
    #serializer_class = SntSNMPEntSerializer

    def delete(self, request, *args, **kwargs):
        id = self.kwargs['pk']
        queryset = monitoring_snmp_entities.objects.all().filter(id=id)

        if queryset.count() > 0:
            queryset.update(status='DELETED')
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'status': "SNMP server not found"}, status=status.HTTP_404_NOT_FOUND)


class SntSmtpCreate(generics.CreateAPIView):
#    queryset = monitoring_smtp.objects.all()
    serializer_class = SntSmtpSerializerCreate
    def post(self, request, *args, **kwargs):
        queryset = monitoring_smtp.objects.filter(component=request.data['component'])

        if queryset.count() > 0:
            queryset.update(smtp_server=request.data['smtp_server'],port=request.data['port'], user_name=request.data['user_name'], password=request.data['password'],sec_type=request.data['sec_type'])
            return Response(monitoring_smtp.objects.values().filter(component=request.data['component']))
        else:
            smtp = monitoring_smtp(smtp_server=request.data['smtp_server'],port=request.data['port'], user_name=request.data['user_name'], password=request.data['password'],component=request.data['component'],sec_type=request.data['sec_type'])
            smtp.save()
            return Response(monitoring_smtp.objects.values().filter(component=request.data['component']))

class SntSmtpList(generics.ListAPIView):
    
    serializer_class = SntSmtpSerializerList

    def get_queryset(self):
        comp  = self.kwargs['component']
        queryset = monitoring_smtp.objects.filter(component=comp)
        return queryset


class SntSmtpDetail(generics.DestroyAPIView):
    queryset = monitoring_smtp.objects.all()
    serializer_class = SntSmtpSerializerList

class SntCredList(generics.ListAPIView):
    
    #serializer_class = SntSmtpSerializerList
    serializer_class = SntSmtpSerializerCred

    def get(self, request, *args, **kwargs):
        smtp = monitoring_smtp.objects.filter(component=self.kwargs['component'])
        if smtp.count() > 0:
            print '1'
            dict = [ obj.as_dict() for obj in smtp]
            psw = (dict[0])['psw']
            psw = base64.b64encode(psw)
            return Response({'status':'key found', 'creds':psw}, status=status.HTTP_200_OK)
        else:
            print '2'
            return Response({'status':'key not found'}, status=status.HTTP_200_OK)


def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError, e:
    return False
  return True

def getPromIP(pop_id_):
    arch = os.environ.get('MON_ARCH','CENTRALIZED')        
    
    pop_id  = pop_id_
    pop = monitoring_pops.objects.values('prom_url').filter(sonata_pop_id=pop_id)
    print pop.count()
    if pop.count() == 0:
        return {'status':'failed', 'msg':'Undefined POP','addr':None}
        #return Response({'status':"Undefined POP"}, status=status.HTTP_404_NOT_FOUND)
    elif pop.count() >1:
        return {'status':'failed', 'msg':'Many POPs with same id','addr':None}
        #return Response({'status':"Many POPs with same id"}, status=status.HTTP_404_NOT_FOUND)
    
    if arch != 'CENTRALIZED':
        prom_url = monitoring_pops.objects.values('prom_url').filter(sonata_pop_id=pop_id)[0]['prom_url']
        print prom_url
        if prom_url == 'undefined':
             return {'status':'failed', 'msg':'Undefined Prometheus address','addr':None}
            #return Response({'status':"Undefined Prometheus address"}, status=status.HTTP_404_NOT_FOUND)
    else:
        prom_url = 'prometheus'
    return {'status':'success', 'msg':'Prometheus address found','addr':prom_url}

class SntPOPList(generics.ListCreateAPIView):
    serializer_class = SntPOPSerializer
    def get_queryset(self):
        queryset = monitoring_pops.objects.all()
        return queryset

    def getCfgfile(self):
        url = 'http://prometheus:9089/prometheus/configuration'
        cl = Http()
        rsp = cl.GET(url,[])
        return rsp

    def postCfgfile(self,confFile):
        url = 'http://prometheus:9089/prometheus/configuration'
        cl = Http()
        rsp = cl.POST(url,[],json.dumps(confFile))            
        return rsp


    def updatePromConf(self, pop):
        arch = os.environ.get('MON_ARCH','CENTRALIZED')
        if arch == 'CENTRALIZED':
            return 200
        updated = False
        file=self.getCfgfile()
        if 'scrape_configs' in file: 
            for obj in file['scrape_configs']:
                if 'target_groups' in obj:
                    for trg in obj['target_groups']:
                        if 'labels' in trg:
                            if 'pop_id' in trg['labels']:
                                if trg['labels']['pop_id'] == pop['sonata_pop_id'] and trg['labels']['sp_id'] ==  pop['sonata_sp_id']:
                                    trg['labels']['name'] =  pop['name']
                                    trg['targets']=[]
                                    trg['targets'].append(pop['prom_url'])
                                    updated = True
                                    continue
            if not updated:
                newTrg={}
                newTrg['labels']={}
                newTrg['labels']['pop_id'] = pop['sonata_pop_id']
                newTrg['labels']['sp_id'] =  pop['sonata_sp_id']
                newTrg['labels']['name'] =  pop['name']
                newTrg['targets']=[]
                newTrg['targets'].append(pop['prom_url'])
                obj['target_groups'].append(newTrg)
        else:
            return 'NOT FOUND scrape_configs'

        if not is_json(json.dumps(file)):
            return Response({'status':"Prometheus reconfiguration failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        code = self.postCfgfile(file)
        return code 

    def post(self, request, *args, **kwargs):
        pop_id = request.data['sonata_pop_id']
        sp_id = request.data['sonata_sp_id']
        name = 'undefined'
        prom_url = 'udefined'
        if 'name' in request.data:
            name = request.data['name']
        if 'prom_url' in request.data:
            prom_url = request.data['prom_url']

        sp = monitoring_service_platforms.objects.all().filter(sonata_sp_id=sp_id)
        if sp.count() == 0:
            sp = monitoring_service_platforms(sonata_sp_id=sp_id, name='undefined', manager_url='127.0.0.1')
            sp.save()
        pop = monitoring_pops.objects.all().filter(sonata_pop_id=pop_id,sonata_sp_id=sp_id)
        if pop.count() == 1:
            #pop = monitoring_pops(sonata_pop_id=pop_id,sonata_sp_id=sp_id, name=name,prom_url=prom_url)
            code = self.updatePromConf(request.data)
            if code == 200:
                pop.update(name=name,prom_url=prom_url)
            else:
                return Response({'status':"Prometheus reconfiguration failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif pop.count()>1:
            return Response({'status':"Many POPs with same id"}, status=status.HTTP_404_NOT_FOUND)
        else:
            code = self.updatePromConf(request.data)
            if code == 200:
                pop = monitoring_pops(sonata_pop_id=pop_id,sonata_sp_id=sp_id, name=name,prom_url=prom_url)
                pop.save()
            else:
                return Response({'status':"Prometheus reconfiguration failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(monitoring_pops.objects.values().filter(sonata_pop_id=pop_id,sonata_sp_id=sp_id))

class SntPOPperSPList(generics.ListAPIView):
    #queryset = monitoring_functions.objects.all()
    serializer_class = SntPOPSerializer

    def get_queryset(self):
        queryset = monitoring_pops.objects.all()
        service_platform_id  = self.kwargs['spID']
        return queryset.filter(sonata_sp_id=service_platform_id)

class SntPOPDetail(generics.DestroyAPIView):
    serializer_class = SntPOPSerializer
    def getCfgfile(self):
        url = 'http://prometheus:9089/prometheus/configuration'
        cl = Http()
        rsp = cl.GET(url,[])
        return rsp

    def postCfgfile(self,confFile):
        url = 'http://prometheus:9089/prometheus/configuration'
        cl = Http()
        rsp = cl.POST(url,[],json.dumps(confFile))            
        return rsp


    def updatePromConf(self, pop_id):
        arch = os.environ.get('MON_ARCH','CENTRALIZED')
        if arch == 'CENTRALIZED':
            return 200
        updated = False
        file=self.getCfgfile()
        if 'scrape_configs' in file: 
            for obj in file['scrape_configs']:
                if 'target_groups' in obj:
                    for trg in obj['target_groups']:
                        if 'labels' in trg:
                            if 'pop_id' in trg['labels']:
                                if trg['labels']['pop_id'] == pop_id:
                                    obj['target_groups'].remove(trg)
                                    updated = True
        else:
            return 'NOT FOUND scrape_configs'

        if not is_json(json.dumps(file)):
            return Response({'status':"Prometheus reconfiguration failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        code = self.postCfgfile(file)
        return code

    
    def delete(self, request, *args, **kwargs):
        #karpa start
        self.lookup_field = 'sonata_pop_id'
        pop_id = self.kwargs['sonata_pop_id']
        queryset = monitoring_pops.objects.all()
        queryset = queryset.filter(sonata_pop_id=pop_id)
        print queryset.count()

        if queryset.count() > 0:
            code = self.updatePromConf(pop_id)
            if code == 200:
                queryset.delete()
                return  Response({'status':"POP removed"}, status=status.HTTP_204_NO_CONTENT)
        else: 
            return  Response({'status':"POP not found"}, status=status.HTTP_404_NOT_FOUND)

class SntSPList(generics.ListCreateAPIView):
    queryset = monitoring_service_platforms.objects.all()
    serializer_class = SntSPSerializer

class SntSPDetail(generics.DestroyAPIView):
    queryset = monitoring_service_platforms.objects.all()
    serializer_class = SntSPSerializer

class SntPromMetricPerPOPList(generics.RetrieveAPIView):
    serializer_class = promMetricsListSerializer
    def get(self, request, *args, **kwargs):
        pop_id = self.kwargs['popID']
        prom_url = getPromIP(pop_id)
        if prom_url['status'] == 'failed':
            return Response({'status': prom_url['msg']}, status=status.HTTP_404_NOT_FOUND)
        mt = ProData(prom_url['addr'],9090)
        data = mt.getMetrics()
        response = {}
        response['metrics'] = data['data']
        print response
        return Response(response)

class SntPromMetricPerPOPDetail(generics.ListAPIView):
    serializer_class = promMetricsListSerializer
    def get(self, request, *args, **kwargs):
        metric_name  = self.kwargs['metricName']
        pop_id = self.kwargs['popID']
        prom_url = getPromIP(pop_id)
        if prom_url['status'] == 'failed':
            return Response({'status': prom_url['msg']}, status=status.HTTP_404_NOT_FOUND)
        mt = ProData(prom_url['addr'],9090)
        data = mt.getMetricDetail(metric_name)
        response = {}
        response['metrics'] = data['data']
        print response
        return Response(response)

class SntPromMetricPerPOPData(generics.CreateAPIView):
    serializer_class = SntPromMetricSerializer
    '''
    {
    "name": "up",
    "start": "2016-02-28T20:10:30.786Z",
    "end": "2016-03-03T20:11:00.781Z",
    "step": "1h",
    "labels": [{"labeltag":"instance", "labelid":"192.168.1.39:9090"},{"labeltag":"group", "labelid":"development"}]
    }
    '''
    def post(self, request, *args, **kwargs):
        pop_id = self.kwargs['popID']
        prom_url = getPromIP(pop_id)
        if prom_url['status'] == 'failed':
            return Response({'status': prom_url['msg']}, status=status.HTTP_404_NOT_FOUND)
        mt = ProData(prom_url['addr'],9090)
        data = mt.getTimeRangeData(request.data)
        response = {}
        #print data
        try:
            response['metrics'] = data['data']
        except KeyError:
            response = data
        return Response(response)

class SntPromSrvPerPOPConf(generics.ListAPIView):
    #start from here
    serializer_class = promMetricsListSerializer
    def get(self, request, *args, **kwargs):
        pop_id = self.kwargs['popID']
        prom_url = getPromIP(pop_id)
        if prom_url['status'] == 'failed':
            return Response({'status': prom_url['msg']}, status=status.HTTP_404_NOT_FOUND)
        url = 'http://'+prom_url['addr']+':9089/prometheus/configuration'
        cl = Http()
        rsp = cl.GET(url,[])
        print rsp
        return Response({'config':rsp}, status=status.HTTP_200_OK)

class SntUserList(generics.ListAPIView):
    serializer_class = SntUserSerializer
    def get_queryset(self):
        queryset = monitoring_users.objects.all()
        userid  = self.kwargs['pk']
        print userid
        return queryset.filter(pk=userid)

class SntUserPerTypeList(generics.ListAPIView):
    #queryset = monitoring_users.objects.all().filter(component=self.kwargs['pk'])
    serializer_class = SntUserSerializer
    def get_queryset(self):
        queryset = monitoring_users.objects.all()
        user_type  = self.kwargs['type']
        return queryset.filter(type=user_type)

class SntUsersList(generics.ListCreateAPIView):
    queryset = monitoring_users.objects.all()
    serializer_class = SntUserSerializer

class SntUsersDetail(generics.DestroyAPIView):
    queryset = monitoring_users.objects.all()
    serializer_class = SntUserSerializer

class SntServicesPerUserList(generics.ListAPIView):
    #queryset = monitoring_services.objects.all().filter(self.kwargs['usrID'])
    serializer_class = SntServicesFullSerializer

    def get_queryset(self):
        queryset = monitoring_services.objects.all()
        userid  = self.kwargs['usrID']
        return queryset.filter(user__sonata_userid=userid)

class SntServiceList(generics.ListAPIView):
    #queryset = monitoring_services.objects.all().filter(self.kwargs['usrID'])
    serializer_class = SntServicesSerializer

    def get_queryset(self):
        queryset = monitoring_services.objects.all()
        srvid  = self.kwargs['srvID']
        return queryset.filter(sonata_srv_id=srvid)

class SntServicesList(generics.ListCreateAPIView):
    queryset = monitoring_services.objects.all()
    serializer_class = SntServicesSerializer

class SntFunctionsPerServiceList(generics.ListAPIView):
    #queryset = monitoring_functions.objects.all()
    serializer_class = SntFunctionsFullSerializer

    def get_queryset(self):
        queryset = monitoring_functions.objects.all() 
        srvid  = self.kwargs['srvID']
        return queryset.filter(service__sonata_srv_id=srvid)

class SntServicesDetail(generics.DestroyAPIView):
    serializer_class = SntServicesDelSerializer

    def delete(self, request, *args, **kwargs):
        self.lookup_field = 'sonata_srv_id'
        queryset = monitoring_services.objects.all()
        srvid  = self.kwargs['sonata_srv_id']
        
        queryset = queryset.filter(sonata_srv_id=srvid)
        print queryset.count()

        if queryset.count() > 0:
            # DELETE also the SNMP entities (if any)
            fcts = monitoring_functions.objects.all().filter(service__sonata_srv_id=srvid)
            if fcts.count() > 0:
                for f in fcts:
                    print f.host_id
                    snmp_entities = monitoring_snmp_entities.objects.all().filter(Q(entity_id=f.host_id) & Q(entity_type='vnf'))
                    if snmp_entities.count() > 0:
                        snmp_entities.update(status='DELETED')
            print 'Network Service deleted ...'
            queryset.delete()
            cl = Http()
            rsp = cl.DELETE('http://prometheus:9089/prometheus/rules/'+str(srvid),[])            
            print rsp
            print 'Service ' +srvid +' removed'
            return  Response({'staus':"service removed"}, status=status.HTTP_204_NO_CONTENT)
        else:
            print 'Service ' +srvid +' not found' 
            return  Response({'status':"service not found"}, status=status.HTTP_404_NOT_FOUND)

class SntFunctionsList(generics.ListAPIView):
    queryset = monitoring_functions.objects.all()
    serializer_class = SntFunctionsSerializer

class SntFunctionsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = monitoring_functions.objects.all()
    serializer_class = SntFunctionsSerializer

class SntNotifTypesList(generics.ListCreateAPIView):
    queryset = monitoring_notif_types.objects.all()
    serializer_class = SntNotifTypeSerializer

class SntNotifTypesDetail(generics.DestroyAPIView):
    queryset = monitoring_notif_types.objects.all()
    serializer_class = SntNotifTypeSerializer

class SntMetricsList(generics.ListAPIView):
    queryset = monitoring_metrics.objects.all()
    serializer_class = SntMetricsSerializer

class SntMetricsPerFunctionList(generics.ListAPIView):
    #queryset = monitoring_metrics.objects.all()
    serializer_class = SntMetricsFullSerializer

    def get_queryset(self):
        queryset = monitoring_metrics.objects.all()
        functionid  = self.kwargs['funcID']
        result_list = list(chain(monitoring_services.objects.all(), monitoring_functions.objects.all(), monitoring_metrics.objects.all()))
        return queryset.filter(function__sonata_func_id=functionid)

class SntMetricsPerFunctionList1(generics.ListAPIView):
    #queryset = monitoring_metrics.objects.all()
    def list(self, request, *args, **kwargs):
        functionid  = kwargs['funcID']
        queryset = monitoring_metrics.objects.all().filter(function_id=functionid)
        dictionaries = [ obj.as_dict() for obj in queryset ]
        response = {}
        response['data_server_url']='http://sp.int2.sonata-nfv.eu:9091'
        response['metrics'] = dictionaries
        return Response(response)

class SntNewServiceConf(generics.CreateAPIView):
    serializer_class = NewServiceSerializer
    def post(self, request, *args, **kwargs):

        if not 'service' in request.data:
            print 'Received new Service notification: Undefined Service'
            return Response({'error':'Undefined Service'}, status=status.HTTP_400_BAD_REQUEST)
        if not 'functions' in request.data:
            print 'Received new Service notification: Undefined Functions'
            return Response({'error':'Undefined Functions'}, status=status.HTTP_400_BAD_REQUEST)
        if not 'rules' in request.data:
            print 'Received new Service notification: Undefined Rules'
            return Response({'error':'Undefined Rules'}, status=status.HTTP_400_BAD_REQUEST)

        print 'Received new Service notification: '+ json.dumps(request.data)

        service = request.data['service']
        functions = request.data['functions']
        rules = request.data['rules']
        functions_status='NULL'
        metrics_status= 'NULL'
        rules_status='NULL'
        oids_status='NULL'

        usr = None
        if 'sonata_usr' in service:
            customer={}
            customer['email'] = None
            customer['phone'] = None

            if 'email' in service['sonata_usr']:
                customer['email'] = service['sonata_usr']['email']
            if 'phone' in service['sonata_usr']:
                customer['phone'] = service['sonata_usr']['phone']

            u = monitoring_users.objects.all().filter(Q(email=customer['email']) & Q(mobile=customer['phone']) & Q(type='cst'))

            if len(u) == 0:
                usr=monitoring_users(mobile=customer['phone'],email=customer['email'],type='cst')
                usr.save()
            else:
                usr = u[0]

        dev = None
        if 'sonata_dev' in service:
            developer = {}
            developer['email'] = None
            developer['phone'] = None
            if 'email' in service['sonata_dev']:
                developer['email']= service['sonata_dev']['email']
            if 'phone' in service['sonata_dev']:
                developer['phone'] = service['sonata_dev']['phone']

            u = monitoring_users.objects.all().filter(Q(email=developer['email']) & Q(mobile=developer['phone']) & Q(type='dev'))

            if len(u) == 0:
                dev=monitoring_users(mobile=developer['phone'],email=developer['email'],type='dev')
                dev.save()
            else:
                dev = u[0]

        '''
        if 'sonata_usr_id' in service:
            if service['sonata_usr_id']:
                u = monitoring_users.objects.all().filter(sonata_userid=service['sonata_usr_id'])             
        else:
            u = monitoring_users.objects.all().filter(sonata_userid='system') 
             
        if u.count() == 0:
            #add new user
            usr = monitoring_users(sonata_userid=service['sonata_usr_id'])
            usr.save()
        else:
            usr = u[0]
        '''

        s = monitoring_services.objects.all().filter(sonata_srv_id=service['sonata_srv_id'])
        if s.count() > 0:
            s.delete()
    
        srv_pop_id = ''
        srv_host_id = ''
        if service['pop_id']: 
            srv_pop_id = service['pop_id']
            pop = monitoring_pops.objects.all().filter(sonata_pop_id=srv_pop_id) 
            if pop.count() == 0: 
                pop = monitoring_pops(sonata_pop_id=srv_pop_id, sonata_sp_id="undefined", name="undefined", prom_url="undefined") #karpa
                pop.save()  
        if service['host_id']: 
            srv_host_id = service['host_id']
        srv = monitoring_services(sonata_srv_id=service['sonata_srv_id'], name=service['name'], description=service['description'], host_id=srv_host_id, pop_id=srv_pop_id)
        srv.save()
        if isinstance(usr, monitoring_users):
            srv.user.add(usr)
        if isinstance(dev, monitoring_users):
            srv.user.add(dev)
        srv.save()

        for f in functions:
            fnc_pop_id = f['pop_id']
            pop = monitoring_pops.objects.all().filter(sonata_pop_id=fnc_pop_id)   
            if pop.count() == 0:    
                pop = monitoring_pops(sonata_pop_id=fnc_pop_id, sonata_sp_id="undefined", name="undefined", prom_url="undefined") 
                pop.save() 
            functions_status=len(functions)
            func = monitoring_functions(service=srv ,host_id=f['host_id'] ,name=f['name'] , sonata_func_id=f['sonata_func_id'] , description=f['description'], pop_id=f['pop_id'])
            func.save()
            for m in f['metrics']:
                metrics_status=len(f['metrics'])
                metric = monitoring_metrics(function=func ,name=m['name'] ,cmd=m['cmd'] ,threshold=m['threshold'] ,interval=m['interval'] ,description=m['description'])
                metric.save()
        
            old_snmps = monitoring_snmp_entities.objects.all().filter(entity_id=f['host_id'])
            if old_snmps.count() > 0:
                old_snmps.update(status='DELETED')

            oids_status = 0
            if 'snmp' in f:
                if len(f['snmp']) > 0:
                    snmp = f['snmp']
                    ent = monitoring_snmp_entities(entity_id=f['host_id'],version=snmp['version'],auth_protocol=snmp['auth_protocol'],security_level=snmp['security_level'],
                                               ip=snmp['ip'],port=161,username=snmp['username'],password='supercalifrajilistico',interval=snmp['interval'],entity_type='vnf')
                    ent.save()
                    oids_status = len(snmp['oids'])
                    for o in snmp['oids']:
                        oid=monitoring_snmp_oids(snmp_entity=ent, oid=o['oid'],metric_name=o['metric_name'],metric_type=o['metric_type'],unit=o['unit'],mib_name=o['mib_name'])
                        oid.save()

        rls = {}
        rls['service'] = service['sonata_srv_id']
        rls['vnf'] = "To be found..."
        rls['rules'] = []  
        for r in rules:
            #print json.dumps(r)
            nt = monitoring_notif_types.objects.all().filter(id=r['notification_type'])
            if nt.count() == 0:
                return Response({'error':'Alert notification type does not supported. Action Aborted'}, status=status.HTTP_400_BAD_REQUEST)
                srv.delete()
            else:
                rules_status=len(rules)
                rule = monitoring_rules(service=srv, summary=r['summary'] ,notification_type=nt[0], name=r['name'] ,condition=r['condition'] ,duration=r['duration'] ,description=r['description'] )
                rule.save()
                rl = {}
                rl['name'] = r['name']
                rl['description'] = r['description']
                rl['summary'] = r['summary']
                rl['duration'] = r['duration']
                rl['notification_type'] = r['notification_type']
                rl['condition'] = r['condition']
                rl['labels'] = ["serviceID=\""+rls['service']+ "\", tp=\"DEV\""]
            rls['rules'].append(rl)

        if len(rules) > 0:
            cl = Http()
            rsp = cl.POST('http://prometheus:9089/prometheus/rules',[],json.dumps(rls))            
            if rsp == 200:
                return Response({'status':"success","vnfs":functions_status,"metrics":metrics_status,"rules":rules_status,"snmp_oids": oids_status})
            else:
                srv.delete()
                return Response({'error': 'Service update fail '+str(rsp)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'status':"success","vnfs":functions_status,"metrics":metrics_status,"rules":rules_status,"snmp_oids": oids_status})

    def getVnfId(funct_,host_):
        for fn in funct_:
            if fn['host_id'] == host_:
                return fn['sonata_func_id']
            else:
                return 'Undefined'

class SntMetricsDetail(generics.DestroyAPIView):
    queryset = monitoring_metrics.objects.all()
    serializer_class = SntMetricsSerializer

class SntRulesList(generics.ListAPIView):
    serializer_class = SntRulesSerializer

    def get_queryset(self):
        queryset = monitoring_rules.objects.all()
        return queryset.filter(consumer='DEV')

class SntRulesPerServiceList(generics.ListAPIView):
    #queryset = monitoring_functions.objects.all()
    serializer_class = SntRulesPerSrvSerializer

    def get_queryset(self):
        queryset = monitoring_rules.objects.all()
        srvid  = self.kwargs['srvID']
        return queryset.filter(service__sonata_srv_id=srvid)


class SntRulesDetail(generics.DestroyAPIView):
    #queryset = monitoring_rules.objects.all()
    serializer_class = SntRulesSerializer

    def delete(self, request, *args, **kwargs):
        queryset = monitoring_rules.objects.all()
        srvid  = self.kwargs['sonata_srv_id']
        fq=queryset.filter(service__sonata_srv_id=srvid)
        print fq
        print fq.count()

        if fq.count() > 0:
            fq.delete()
            cl = Http()
            rsp = cl.DELETE('http://prometheus:9089/prometheus/rules/' + str(srvid), [])
            rsp = cl.DELETE('http://prometheus:9089/prometheus/rules/' + str('plc-'+srvid), [])
            rsp = cl.DELETE('http://prometheus:9089/prometheus/rules/' + str('sla-'+srvid), [])
            return  Response({'status': "Service's rules removed (inl. SLA, POLICY)"}, status=status.HTTP_204_NO_CONTENT)
        else: 
            return  Response({'status':"rules not found"}, status=status.HTTP_404_NOT_FOUND)

class SntPromMetricList(generics.RetrieveAPIView):
    serializer_class = promMetricsListSerializer
    def get(self, request, *args, **kwargs):
        mt = ProData('prometheus',9090)
        data = mt.getMetrics()
        response = {}
        response['metrics'] = data['data']
        #print response
        return Response(response)

class SntPromMetricListVnf(generics.RetrieveAPIView):
    serializer_class = promMetricsListSerializer
    def get(self, request, *args, **kwargs):
        mt = ProData('prometheus',9090)
        vnfid = self.kwargs['vnf_id']
        queryset = monitoring_functions.objects.all()
        vnf=queryset.filter(sonata_func_id=vnfid)
        response = {}
        if vnf.count() == 0:
            response['status'] = "Fail (VNF not found)"
            return Response(response)
        vdus = []
        vdus.append(vnf[0].host_id)
        #print (vdus)
        response['status'] = 'Success'
        response['vdus'] = []
        for vdu in vdus:
            dt = {}
            dt['vdu_id'] = vdu
            data = mt.getMetricsResId(vdu)
            if 'data' in data:
                dt['metrics'] = data['data']
            else:
                dt['metrics'] = []
            response['vdus'].append(dt)
        return Response(response)

class SntPromMetricListVnfVdu(generics.RetrieveAPIView):
    serializer_class = promMetricsListSerializer
    def get(self, request, *args, **kwargs):
        mt = ProData('prometheus',9090)
        vnfid = self.kwargs['vnf_id']
        vduid = self.kwargs['vdu_id']
        queryset = monitoring_functions.objects.all()
        vnf=queryset.filter(sonata_func_id=vnfid)
        response = {}
        if vnf.count() == 0:
            response['status'] = "Fail (VNF: "+vnfid+" not found)"
            return Response(response)
        vdus = []
        vdus.append(vnf[0].host_id)
        if vduid not in vdus:
            response['status'] = "Fail (VDU: "+vduid+" doesn't belong in VNF:"+vnfid+")"
            return Response(response)
        response['status'] = 'Success'
        response['vdus'] = []
        for vdu in vdus:
            dt = {}
            dt['vdu_id'] = vdu
            data = mt.getMetricsResId(vdu)
            if 'data' in data:
                dt['metrics'] = data['data']
            else:
                dt['metrics'] = []
            response['vdus'].append(dt)
        return Response(response)

class SntPromVnfMetricDetail(generics.ListAPIView):
    serializer_class = promMetricsListSerializer
    def get(self, request, *args, **kwargs):
        metric_name  = self.kwargs['metricName']
        vnfid = self.kwargs['vnf_id']
        mt = ProData('prometheus',9090)
        queryset = monitoring_functions.objects.all()
        vnf = queryset.filter(sonata_func_id=vnfid)
        response = {}
        if vnf.count() == 0:
            response['status'] = "Fail (VNF: " + vnfid + " not found)"
            return Response(response)
        vdus = []
        vdus.append(vnf[0].host_id)
        response['status'] = 'Success'
        response['vdus'] = []
        for vdu in vdus:
            dt={}
            dt['vdu_id'] = vdu
            data = mt.getMetricDetail(vdu,metric_name)
            if 'data' in data:
                dt['metrics'] = data['data']['result']
            else:
                dt['metrics'] = []
            response['vdus'].append(dt)
        return Response(response)

class SntWSreq(generics.CreateAPIView):
    serializer_class = SntWSreqSerializer

    def post(self, request, *args, **kwargs):
        filters = []
        psw = socket.gethostbyname('pushgateway')
        if 'filters' in request.data.keys():
            filters = request.data['filters']
        metric = request.data['metric']
        url = "http://"+psw+":8002/new/?metric="+metric+"&params="+json.dumps(filters).replace(" ", "")
        print url
        cl = Http()
        rsp = cl.GET(url,[])
        print url
        response = {}
        try:
            if 'name_space' in rsp:
                response['status'] = "SUCCESS"
                response['metric'] = request.data['metric']
                response['ws_url'] = "ws://"+psw+":8002/ws/"+str(rsp['name_space'])
            else:
                response['status'] = "FAIL"
                response['ws_url'] = None
        except KeyError:
            response = data
            pass
        return Response(response)

class SntWSreqPerPOP(generics.CreateAPIView):
    serializer_class = SntWSreqSerializer

    def post(self, request, *args, **kwargs):
        filters = []
        if 'filters' in request.data.keys():
            filters = request.data['filters']
        metric = request.data['metric']
        pop_id = self.kwargs['popID']
        prom_url = getPromIP(pop_id)
        if prom_url['status'] == 'failed':
            return Response({'status': prom_url['msg']}, status=status.HTTP_404_NOT_FOUND)
        ip = socket.gethostbyname(prom_url['addr'])
        url = "http://"+ip+":8002/new/?metric="+metric+"&params="+json.dumps(filters).replace(" ", "")
        #print url
        cl = Http()
        rsp = cl.GET(url,[])
        print rsp
        response = {}
        try:
            if 'name_space' in rsp:
                response['status'] = "SUCCESS"
                response['metric'] = request.data['metric']
                response['ws_url'] = "ws://"+ip+":8002/ws/"+str(rsp['name_space'])
            else:
                response['status'] = "FAIL"
                response['ws_url'] = None
        except KeyError:
            response = data
            pass
        return Response(response)

class SntRuleconf(generics.CreateAPIView):
    serializer_class = SntRulesConfSerializer

    def post(self, request, *args, **kwargs):
        srvid  = self.kwargs['srvID']
        if 'rules' in request.data.keys():
            rules = request.data['rules']
        else:
            return Response({'error':'Undefined rules'}, status=status.HTTP_400_BAD_REQUEST)
        
        #Check if service exists
        srv = monitoring_services.objects.all().filter(sonata_srv_id=srvid)

        if srv.count() == 0:
            if srvid != 'generic':
                return Response({'error':'Requested Service not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                srvid = 'alerts'

        #Delete old rule from DB
        rules_db = monitoring_rules.objects.all().filter(service__sonata_srv_id=srvid, consumer='DEV')
        rules_db.delete()

        #Create prometheus configuration file 
        rls = {}
        rls['service'] = srvid
        rls['vnf'] = "To be found..."
        rls['rules'] = []  
        rules_status=len(rules)
        for r in rules:
            #print json.dumps(r)
            nt = monitoring_notif_types.objects.all().filter(id=r['notification_type'])
            if nt.count() == 0:
                return Response({'error':'Alert notification type does not supported. Action Aborted'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if srvid != "alerts":
                    rule = monitoring_rules(service=srv[0], summary=r['summary'] ,notification_type=nt[0], name=r['name'] ,condition=r['condition'] ,duration=r['duration'] ,description=r['description'] )
                    rule.save()
                rl = {}
                rl['name'] = r['name']
                rl['description'] = r['description']
                rl['summary'] = r['summary']
                rl['duration'] = r['duration']
                rl['notification_type'] = r['notification_type']
                rl['condition'] = r['condition']
                rl['labels'] = ["serviceID=\"" + rls['service'] + "\", tp=\"DEV\""]
            rls['rules'].append(rl)


        if len(rules) > 0:
            cl = Http()
            rsp = cl.POST('http://prometheus:9089/prometheus/rules',[],json.dumps(rls))            
            if rsp == 200:
                return Response({'status':"success","rules":rules_status})
            else:
                return Response({'error': 'Rule update failed '+str(rsp)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'No rules defined'})

class SntPromMetricData(generics.CreateAPIView):
    serializer_class = SntPromMetricSerializer
    '''
    {
    "name": "up",
    "start": "2016-02-28T20:10:30.786Z",
    "end": "2016-03-03T20:11:00.781Z",
    "step": "1h",
    "labels": [{"labeltag":"instance", "labelid":"192.168.1.39:9090"},{"labeltag":"group", "labelid":"development"}]
    }
    '''
    def post(self, request, *args, **kwargs):
        mt = ProData('prometheus',9090)
        data = mt.getTimeRangeData(request.data)
        response = {}
        #print data
        try:
            response['metrics'] = data['data']
        except KeyError:
            response = data
        return Response(response)

class SntPromMetricDataPerVnf(generics.CreateAPIView):
    serializer_class = SntPromMetricSerializer
    

    def post(self, request, *args, **kwargs):
        mt = ProData('prometheus', 9090)
        vnfid = self.kwargs['vnf_id']
        queryset = monitoring_functions.objects.all()
        vnf = queryset.filter(sonata_func_id=vnfid)
        request.data["labels"] = [{"labeltag":"resource_id", "labelid":vnf[0].host_id}]
        data = mt.getTimeRangeDataVnf(request.data)
        response = {}
        # print data
        try:
            response['metrics'] = data['data']
        except KeyError:
            response = data
        return Response(response)

class SntPromMetricDetail(generics.ListAPIView):
    serializer_class = promMetricsListSerializer
    def get(self, request, *args, **kwargs):
        metric_name  = self.kwargs['metricName']
        mt = ProData('prometheus',9090)
        data = mt.getMetricDetail(metric_name)
        response = {}
        response['metrics'] = data['data']
        print response
        return Response(response)

class SntPromSrvConf(generics.ListAPIView):
    #start from here
    def get(self, request, *args, **kwargs):
        url = 'http://prometheus:9089/prometheus/configuration'
        cl = Http()
        rsp = cl.GET(url,[])
        print rsp
        return Response({'config':rsp}, status=status.HTTP_200_OK)

 
class SntActMRList(generics.ListAPIView):
    serializer_class = SntActMonResSerializer

    def get_queryset(self):
        queryset = active_monitoring_res.objects.all()
        service_id_ = self.kwargs['service_id']
        return queryset.filter(service_id = service_id_)

class SntActMRDelete(generics.DestroyAPIView):
    serializer_class = SntActMonResSerializer

    def delete(self, request, *args, **kwargs):
        self.lookup_field = 'service_id'
        queryset = active_monitoring_res.objects.all()
        srvid = self.kwargs['service_id']
        queryset = queryset.filter(service_id=srvid)

        if queryset.count() > 0:
            queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'status': "Results not found"}, status=status.HTTP_404_NOT_FOUND)

class SntActMRDetail(generics.ListAPIView):
    serializer_class = SntActMonResDetailSerializer

    def get_queryset(self):
        queryset = active_monitoring_res.objects.all()
        service_id_ = self.kwargs['service_id']
        test_id_ = self.kwargs['test_id']
        return queryset.filter(service_id = service_id_,test_id = test_id_)

class SntActMRDt(generics.CreateAPIView):
    serializer_class = SntActMonResDataSerializer

    def post(self, request, *args, **kwargs):
        queryset = active_monitoring_res.objects.all()
        service_id_ = self.kwargs['service_id']
        test_id_ = self.kwargs['test_id']
        data_ = request.data
        fl_test_id_ = data_['TestID']
        tmstp_ = data_['Timestamp']
        cnfg_ = data_['TestConfig']
        print(service_id_)
        print(test_id_)
        tm=datetime.datetime.utcfromtimestamp(float(tmstp_)).strftime('%Y-%m-%d %H:%M:%S')
        try:
            data = active_monitoring_res(test_id=test_id_,service_id=service_id_, timestamp=tm, config=cnfg_, data=data_)
            data.save()
        except IntegrityError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'id': fl_test_id_,'timestamp':tm,'configuration':cnfg_}, status=status.HTTP_200_OK)

class Ping(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        p = psutil.Process(os.getpid())
        uptime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.create_time())) + ' UTC'
        return Response({'alive_since':uptime}, status=status.HTTP_200_OK)