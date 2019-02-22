import json, yaml, datetime, time
from typing import Dict, List, Any, Union

from django.db import IntegrityError
from django.db.models import Q
from api.models import *
from api.httpClient import Http


class Sonata(object):

    def __init__(self):
        self.mano_type = 'sonata'
        pass

    def ns_descriptor(self, nsd):
        nsdesc = nsd['NSD']
        if 'network_functions' in nsdesc:
            index = 0
            for vnf in nsdesc['network_functions']:
                lb = 'VNFD' + str(index)
                if lb in nsd:
                    v = vnf_descriptors.objects.filter(Q(vnfd_id=nsd[lb]['uuid']) & Q(version=nsd[lb]['version']) &
                                                       Q(mano_type=self.mano_type))
                    if v.count() > 0:
                        v.delete()

                    try:
                        data = vnf_descriptors(vnfd_id=nsd[lb]['uuid'], version=nsd[lb]['version'],
                                               mano_type=self.mano_type,
                                               data=json.dumps(nsd[lb], sort_keys=True, indent=2))
                        data.save()
                    except IntegrityError as e:
                        pass
                index += 1
        js_obj = json.dumps(nsd, sort_keys=True, indent=2)
        print(js_obj)
        n = ns_descriptors.objects.filter(Q(nsd_id=nsd['NSD']['uuid']) &
                                          Q(version=nsd['NSD']['version']) &
                                          Q(mano_type=self.mano_type))
        if n.count() > 0:
            n.delete()

        try:
            data = ns_descriptors(nsd_id=nsd['NSD']['uuid'], version=nsd['NSD']['version'],
                                  mano_type=self.mano_type, data=js_obj)
            data.save()
        except IntegrityError as e:
            pass

    def ns_records(self, nsr):
        # Get NS descriptor
        nsd_r = ns_descriptors.objects.filter(Q(nsd_id=nsr['nsr']['descriptor_reference']) &
                                              Q(mano_type=self.mano_type))
        if len(nsd_r) == 0:
            print('NO NSD available....')
            return
        nsd = json.loads(nsd_r.get().data)

        # Get VNF descriptor
        if 'vnfrs' in nsr:
            vnfds = {}
            for vnfr in nsr['vnfrs']:
                vnfdesc = vnf_descriptors.objects.filter(Q(vnfd_id=vnfr['descriptor_reference']) &
                                                         Q(mano_type=self.mano_type))

                if len(vnfdesc) == 0:
                    print('NO VNFD available.... ' + vnfr['descriptor_reference'])
                    return
                desc = json.loads(vnfdesc.get().data)
                vnfds[desc['uuid']] = desc
        # Clear service
        s = monitoring_services.objects.all().filter(sonata_srv_id=nsr['nsr']['id'])
        if s.count() > 0:
            s.delete()

        # Store new NS
        srv = monitoring_services(sonata_srv_id=nsr['nsr']['id'], name=nsd['NSD']['name'],
                                  description=nsd['NSD']['description'])
        srv.save()

        # Store new VNFS
        oids_status = 0
        metrics_status = 0
        vdus = {}
        for vnfr in nsr['vnfrs']:

            functions_status = len(nsr['vnfrs'])
            for vdu in vnfr['virtual_deployment_units']:
                vdu_id = vdu['id']
                vdu_ip = None
                for vnfc_instance in vdu['vnfc_instance']:
                    if 'connection_points' in vnfc_instance:
                        for inf in vnfc_instance['connection_points']:
                            if inf['type'] == 'management':
                                vdu_ip = inf['interface']['address']
                                continue
                    vdus[vdu_id] = vnfc_instance['vc_id']
                    fnc_pop_id = vnfc_instance['vim_id']
                    pop = monitoring_pops.objects.all().filter(sonata_pop_id=fnc_pop_id)
                    if pop.count() == 0:
                        pop = monitoring_pops(sonata_pop_id=fnc_pop_id, sonata_sp_id="undefined", name="undefined",
                                              prom_url="undefined")
                        pop.save()
                    func = monitoring_functions(service=srv, host_id=vnfc_instance['vc_id'],
                                                name=vnfds[vnfr['descriptor_reference']]['name'],
                                                sonata_func_id=vnfr['id'],
                                                description=vnfds[vnfr['descriptor_reference']]['description'],
                                                pop_id=vnfc_instance['vim_id'])
                    func.save()

                    vduds = vnfds[vnfr['descriptor_reference']]['virtual_deployment_units']
                    for vdud in vduds:
                        if vdud['id'] == vdu_id:
                            if 'monitoring_parameters' in vdud:
                                metrics = vdud['monitoring_parameters']
                                for m in metrics:
                                    if 'name' in m and 'unit' in m:
                                        metrics_status += 1
                                        metric = monitoring_metrics(function=func, name=m['name'],
                                                                    description=m['unit'])
                                        metric.save()
                                    elif 'name' in m:
                                        metrics_status += 1
                                        metric = monitoring_metrics(function=func, name=m['name'],
                                                                    description=m['unit'])
                                        metric.save()
                                print(metrics)
                            if 'snmp_parameters' in vdud:
                                if vdu_ip == None:
                                    print('No management port found to access the snmp server...')
                                snmp = vdud['snmp_parameters']
                                old_snmps = monitoring_snmp_entities.objects.all().filter(
                                    entity_id=vnfc_instance['vc_id'])
                                if old_snmps.count() > 0:
                                    old_snmps.update(status='DELETED')

                                if 'port' in snmp:
                                    port = snmp['port']
                                else:
                                    port = 161
                                if 'password' in snmp:
                                    pwd = snmp['password']
                                else:
                                    pwd = 'supercalifrajilistico'
                                    ent = monitoring_snmp_entities(entity_id=vnfc_instance['vc_id'],
                                                                   version=snmp['version'],
                                                                   auth_protocol=snmp['auth_protocol'],
                                                                   security_level=snmp['security_level'],
                                                                   ip=vdu_ip, port=port,
                                                                   username=snmp['username'],
                                                                   password=pwd,
                                                                   interval=snmp['interval'], entity_type='vnf')
                                    ent.save()

                                    for o in snmp['oids']:
                                        oid = monitoring_snmp_oids(snmp_entity=ent, oid=o['oid'],
                                                                   metric_name=o['metric_name'],
                                                                   metric_type=o['metric_type'],
                                                                   unit=o['unit'],
                                                                   mib_name=o['mib_name'])
                                        oid.save()
                                        oids_status += 1

                                print(snmp)

        if 'monitoring_rules' in vnfds[vnfr['descriptor_reference']]:
            rls = {}
            rls['service'] = nsr['nsr']['id']
            rls['rules'] = []
            rules = vnfds[vnfr['descriptor_reference']]['monitoring_rules']
            for r in rules:
                nt = monitoring_notif_types.objects.all().filter(type='rabbitmq')
                if nt.count() == 0:
                    print("'error': 'Alert notification type does not supported. Action Aborted'")
                    srv.delete()
                vdu_id, condition = r['condition'].split(':')
                if vdu_id in vdus:
                    r['condition'] = vdus[vdu_id] + ':' + condition
                else:
                    print("'error': 'vdu_id: %s didn't found...", vdu_id)
                    continue
                if 'summary' not in r:
                    r['summary'] = ' '
                rl = {'name': r['name'], 'description': r['description'], 'summary': r['summary'],
                      'duration': str(r['duration']) + r['duration_unit'], 'notification_type': 'rabbitmq',
                      'condition': r['condition'],
                      'labels': ["serviceID=\"" + rls['service'] + "\", tp=\"DEV\""]}
                rules_status = len(rules)
                rule = monitoring_rules(service=srv, summary=r['summary'], notification_type=nt[0], name=r['name'],
                                        condition=r['condition'], duration=r['duration'],
                                        description=r['description'])
                rule.save()
                rls['rules'].append(rl)

            print(rules)
            if len(rules) > 0:
                cl = Http()
                print(json.dumps(rls))
                rsp = cl.POST(url_='http://prometheus:9089/prometheus/rules', headers_=[], data_=json.dumps(rls))
                if rsp == 200:
                    print(
                        "{'status': 'success', 'vnfs: %s, 'metrics': %s,'rules': %s, 'snmp_oids': %s}"
                        % (str(functions_status),
                           str(metrics_status),
                           str(rules_status),
                           str(oids_status)))
                else:
                    srv.delete()
                    rsp['status'] = 'failed'
                    return print(str(rsp))
            else:
                print(
                    "{'status': 'success', 'vnfs: %s, 'metrics': %s,'rules': %s, 'snmp_oids': %s}"
                    % (str(functions_status),
                       str(metrics_status),
                       str(rules_status),
                       str(oids_status)))


    def ns_termination(self, msg):
        ns_id = 'to be defined'
        queryset = monitoring_services.objects.all().filter(sonata_srv_id=ns_id)
        print(queryset.count())

        if queryset.count() > 0:
            # DELETE also the SNMP entities (if any)
            fcts = monitoring_functions.objects.all().filter(service__sonata_srv_id=ns_id)
            if fcts.count() > 0:
                for f in fcts:
                    print(f.host_id)
                    snmp_entities = monitoring_snmp_entities.objects.all().filter(
                        Q(entity_id=f.host_id) & Q(entity_type='vnf'))
                    if snmp_entities.count() > 0:
                        snmp_entities.update(status='DELETED')
            print('Network Service deteted ...')
            queryset.delete()
            cl = Http()
            rsp = cl.DELETE('http://prometheus:9089/prometheus/rules/' + str(ns_id), [])
            print(rsp)
            print('Service ' + ns_id + ' removed')
            time.sleep(2)
            rsp = cl.DELETE('http://prometheus:9089/prometheus/rules/sla-' + str(ns_id), [])
            print(rsp)
            time.sleep(2)
            rsp = cl.DELETE('http://prometheus:9089/prometheus/rules/plc-' + str(ns_id), [])
            print({'status': 'service removed'})
        else:
            print({'status': 'Service ' + ns_id + ' not found'})
