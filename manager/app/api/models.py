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

from __future__ import unicode_literals

from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight
from datetime import datetime
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

# Create your models here.
LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())


class monitoring_snmp_entities(models.Model):
    VER = (('v3', 'v3'),('v2', 'v2'),('v1', 'v1'),)
    AUTH_PROT = (('MD5', 'MD5'),('None', 'None'),)
    SEC_LEV = (('authnoPriv', 'authnoPriv'),('None', 'None'),)
    STATUS = (('UPDATED', 'UPDATED'), ('DISABLED', 'DISABLED'),)
    ip = models.GenericIPAddressField(default={})
    port = models.CharField(max_length=6, blank=False)
    interval = models.CharField(max_length=5, blank=False)
    entity_type = models.CharField(max_length=60, blank=False)
    entity_id = models.CharField(max_length=36, blank=False)
    version = models.CharField(max_length=5, choices=VER)
    #oids = models.ManyToManyField(monitoring_snmp_oids)
    auth_protocol = models.CharField(max_length=5, choices=AUTH_PROT)
    security_level = models.CharField(max_length=15, choices=SEC_LEV)
    status = models.CharField(max_length=10, default='UPDATED')
    username = models.CharField(max_length=60, blank=False)
    password = models.CharField(max_length=60, blank=False)
    created = models.DateTimeField(default=timezone.now)

    def as_dict(self):
        return {
            'ip': self.ip,
            'port': self.port,
            'interval':self.interval,
            'entity_type':self.component,
            'entity_id':self.entity_id,
            'version':self.version,
            'oids':self.oids,
            'auth_protocol':self.auth_protocol,
            'security_level':self.security_level,
            'status':self.STATUS,
            'username':self.username,
            'password':self.password,
            'created':self.created
            # other stuff
        }

    class Meta:
        db_table = "monitoring_snmp_entities"
        ordering = ('created',)
        managed = True

    def __unicode__(self):
        return u'%s %s %s' % (self.ip, self.port, self.entity_id, self.entity_type)


class monitoring_snmp_oids(models.Model):
    MT_TYPE = (('gauge', 'gauge'),)
    snmp_entity = models.ForeignKey(monitoring_snmp_entities, related_name='oids', on_delete=models.CASCADE)
    oid = models.CharField(max_length=512, blank=False)
    metric_name = models.CharField(max_length=60, blank=False)
    metric_type = models.CharField(max_length=10, choices=MT_TYPE)
    unit = models.CharField(max_length=30, blank=False)
    mib_name = models.CharField(max_length=512, blank=False)
    created = models.DateTimeField(default=timezone.now)

    def as_dict(self):
        return {
            'oid': self.oid,
            'metric_name':self.metric_name,
            'metric_type':self.metric_type,
            'unit':self.unit,
            'mib_name':self.mib_name,
            'created':self.created
            # other stuff
        }

    class Meta:
        db_table = "monitoring_snmp_oids"
        ordering = ('created',)
        managed = True

    def __unicode__(self):
        return u'%s %s %s' % (self.metric_name, self.id, self.oid)


class monitoring_smtp(models.Model):
    SEC_TYPES = (
        ('SSL', 'SSL'),
        ('TLS', 'TLS'),
        ('SSL_ALL', 'SSL_ALL_CERTS'),
        ('TLS_ALL', 'TLS_ALL_CERTS'),
        )
    COMPS = (('Alert_Manager','Alert_Manager'),)
    smtp_server = models.CharField(max_length=30, blank=True)
    port = models.CharField(max_length=30, blank=True)
    user_name = models.EmailField(blank=True)
    password = models.CharField(max_length=60)
    component = models.CharField(max_length=60, choices=COMPS)
    sec_type = models.CharField(max_length=20, choices=SEC_TYPES)
    created = models.DateTimeField(default=timezone.now)

    def as_dict(self):
        return {
            'id': self.id,
            'smtp_server': self.smtp_server,
            'port': self.port,
            'user_name':self.user_name,
            'component':self.component,
            'sec_type':self.sec_type,
            'psw':self.password,
            'created':self.created
            # other stuff
        }  

    class Meta:
        db_table = "monitoring_smtp"
        ordering = ('created',)
        managed = True

    def __unicode__(self):
        return u'%s %s %s %s %s' % (self.smtp_server, self.port, self.user_name, self.component, self.sec_type)

class monitoring_service_platforms(models.Model):
    name = models.CharField(max_length=30, blank=True)
    manager_url = models.CharField(max_length=128, blank=True)
    sonata_sp_id = models.CharField(max_length=60)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "monitoring_service_platforms"
        ordering = ('created',)
        managed = True

    def __unicode__(self):
        return u'%s %s %s' % (self.name, self.manager_url, self.sonata_sp_id)

class monitoring_pops(models.Model):
    name = models.CharField(max_length=30, blank=True)
    prom_url = models.CharField(max_length=128, blank=True)
    sonata_sp_id = models.CharField(max_length=60)
    sonata_pop_id = models.CharField(max_length=60)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "monitoring_pops"
        ordering = ('created',)
        managed = True

    def __unicode__(self):
        return u'%s %s %s %s' % (self.name, self.prom_url, self.sonata_pop_id, self.sonata_sp_id)

class monitoring_users(models.Model):
    USR_TYPES = (('cst', 'customer'), ('dev', 'developer'), ('admin', "admin"),)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True, null=True)
    mobile = models.DecimalField(max_digits=13, decimal_places=0, null=True, blank=True)
    type = models.CharField(max_length=60, choices=USR_TYPES, null=True)
    sonata_userid = models.CharField(max_length=60, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now, null=True)

    class Meta:
        db_table = "monitoring_users"
        ordering = ('created',)
        managed = True

    def __unicode__(self):
        return u'%s %s %s' % (self.first_name, self.last_name, self.sonata_userid)

class monitoring_services(models.Model):
    user = models.ManyToManyField(monitoring_users)
    pop_id = models.CharField(max_length=60, blank=True)
    host_id = models.CharField(max_length=60, blank=True)
    name = models.CharField(max_length=30, blank=True)
    sonata_srv_id = models.CharField(max_length=60, blank=True)
    description = models.CharField(max_length=1024)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "monitoring_services"
        ordering = ('created',)
        managed = True

    def __unicode__(self):
        return u'%s %s %s' % (self.name, self.description, self.sonata_srv_id)


class monitoring_functions(models.Model):
    service = models.ForeignKey(monitoring_services)
    pop_id = models.CharField(max_length=60, blank=True)
    host_id = models.CharField(max_length=60, blank=True)
    host_type = models.CharField(max_length=60, blank=True)
    name = models.CharField(max_length=30, blank=True)
    sonata_func_id = models.CharField(max_length=60, blank=True)
    description = models.CharField(max_length=1024)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "monitoring_functions"
        ordering = ('created',)
        managed = True

    def __unicode__(self):
        return u'%s %s %s' % (self.name, self.description, self.sonata_func_id)

class monitoring_metrics(models.Model):
    function = models.ForeignKey(monitoring_functions)
    name = models.CharField(max_length=30, blank=True)
    cmd = models.CharField(max_length=1024, null=True)
    threshold = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    interval = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    description = models.CharField(max_length=1024, null=True)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "monitoring_metrics"
        ordering = ('created',)
        managed = True

    def as_dict(self):
        return {
            #'function': self.function['id'],
            'name': self.name,
            'cmd': self.cmd,
            'threshold':self.threshold,
            'interval':self.interval,
            'description':self.description,
            'created':self.created
            # other stuff
        }  

    def __unicode__(self):
        return u'%s %s %s' % (self.name, self.description, self.cmd)

class monitoring_notif_types(models.Model):
    type = models.CharField(max_length=30, blank=True)

    class Meta:
        db_table = "monitoring_notif_types"
        managed = True

    def __unicode__(self):
        return u'%s %s' % (self.id, self.type)

class monitoring_rules(models.Model):
    VER = (('DEV','DEV'),('SLA', 'SLA'), ('PLC','PLC'),)
    service = models.ForeignKey(monitoring_services)
    function = models.CharField(max_length=60, blank=True)
    vdu = models.CharField(max_length=36, blank=True)
    summary = models.CharField(max_length=1024, blank=True)
    consumer = models.CharField(max_length=5, choices=VER, default='DEV')
    notification_type = models.ForeignKey(monitoring_notif_types)
    name = models.CharField(max_length=60, blank=True)
    condition = models.CharField(max_length=2048, blank=False)
    duration = models.CharField(max_length=30, blank=False)
    description = models.CharField(max_length=2048)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "monitoring_rules"
        ordering = ('created',)
        managed = True

    def __unicode__(self):
        return u'%s %s  %s %s' % (self.name, self.description, self.condition, str(self.service))

class prom_metric(object):
    def __init__(self, name):
        self.name = name

    def __unicode__(self):
        return u'%s' % (self.name)


class active_monitoring_res(models.Model):
    test_id = models.CharField(max_length=300, blank=False, unique=True)
    service_id = models.CharField(max_length=300, blank=False)
    timestamp = models.DateTimeField(default=timezone.now)
    config = JSONField()
    data = JSONField()

    def __str__(self):
        return self.test_id


#rq = {'metric':'prometheus_data_size','labels':[{'instanseID':'jdhfksdhfk'}],'start':'2016-02-01T20:10:30.786Z', 'end':'2016-02-28T20:11:00.781Z', 'step':'1h'}


class ServiceConf(object):
    def __init__(self, service, functions, metrics, rules, created=None):
        self.service = service
        self.functions = functions
        self.metrics = metrics
        self.rules = rules
