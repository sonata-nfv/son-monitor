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

from rest_framework import serializers
from api.models import *
from api.serializers import *
from django.contrib.auth.models import User
from django.core import serializers as core_serializers


#######################################################################################################

class SntPasMonResDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = passive_monitoring_res
        fields = ('service_id','test_id','created','terminated','data')

class SntPasMonResSerializer(serializers.ModelSerializer):
    class Meta:
        model = passive_monitoring_res
        fields = ('service_id','test_id','created','terminated')

class SntSNMPOidSerializer(serializers.ModelSerializer):
    class Meta:
        model = monitoring_snmp_oids
        fields = ('oid', 'metric_name', 'metric_type', 'unit', 'mib_name')

class SntSNMPEntSerializer(serializers.ModelSerializer):
    #user = serializers.PrimaryKeyRelatedField(read_only=False, queryset=monitoring_users.objects.all())
    #user = SntUserSerializer()
    oids = SntSNMPOidSerializer(many=True)

    class Meta:
        model = monitoring_snmp_entities
        fields = ('id', 'ip', 'port','username', 'interval', 'entity_type','oids' , 'entity_id', 'version', 'auth_protocol', 'security_level', 'status')


class SntSNMPEntFullSerializer(serializers.ModelSerializer):
    oids = SntSNMPOidSerializer(many=True)

    class Meta:
        model = monitoring_snmp_entities
        fields = ('id', 'ip', 'port','username', 'password', 'interval', 'entity_type','oids' , 'entity_id', 'version', 'auth_protocol', 'security_level', 'status')
        lookup_field = {'ip', 'port'}

    def create(self, validated_data):
        oids_data = validated_data.pop('oids')
        ent_ip = validated_data['ip']
        ent_port = validated_data['port']
        ent = monitoring_snmp_entities.objects.all().filter(ip=ent_ip,port=ent_port)
        print (ent.count())
        if ent.count() > 0:
            ent.delete()
        entity = monitoring_snmp_entities.objects.create(**validated_data)
        for oid in oids_data:
            monitoring_snmp_oids.objects.create(snmp_entity=entity, **oid)
        return entity



class SntSmtpSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = monitoring_smtp
        fields = ('id', 'smtp_server', 'port', 'user_name', 'password', 'component', 'sec_type') 

class SntSmtpSerializerList(serializers.ModelSerializer):
    class Meta:
        model = monitoring_smtp
        fields = ('id', 'smtp_server', 'port', 'user_name', 'component', 'sec_type', 'created') 

class SntSmtpSerializerCred(serializers.ModelSerializer):
    class Meta:
        model = monitoring_smtp
        fields = ('id', 'password') 

class SntSPSerializer(serializers.ModelSerializer):
    class Meta:
        model = monitoring_service_platforms
        fields = ('id', 'sonata_sp_id', 'name', 'manager_url','created')

class SntPOPSerializer(serializers.ModelSerializer):
    class Meta:
        model = monitoring_pops
        fields = ('id', 'sonata_pop_id','sonata_sp_id' ,'name', 'prom_url','created')
        lookup_field = 'sonata_pop_id'

class SntUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = monitoring_users
        fields = ('id', 'first_name', 'last_name', 'email', 'sonata_userid', 'created','type','mobile')
        lookup_field = {'email','mobile'}


class SntServicesSerializer(serializers.ModelSerializer):
    #user = serializers.PrimaryKeyRelatedField(read_only=False, queryset=monitoring_users.objects.all())
    #user = SntUserSerializer()
    ns_instance_id = serializers.CharField(source='sonata_srv_id')
    test_id = serializers.CharField(source='description')
    class Meta:
        model = monitoring_services
        fields = ('ns_instance_id', 'test_id','created','terminated')

class SntServicesFullSerializer(serializers.ModelSerializer):
    #user = serializers.PrimaryKeyRelatedField(read_only=False, queryset=monitoring_users.objects.all())
    user = SntUserSerializer()
    class Meta:
        model = monitoring_services
        fields = ('id', 'sonata_srv_id', 'name', 'description', 'created', 'user', 'host_id','pop_id')

class SntFunctionsSerializer(serializers.ModelSerializer):
    service = serializers.PrimaryKeyRelatedField(read_only=False, queryset=monitoring_services.objects.all())
    #service = SntServicesSerializer()
    class Meta:
        model = monitoring_functions
        fields = ('id', 'sonata_func_id', 'name', 'description', 'created', 'service', 'host_id','pop_id')

class SntServicesDelSerializer(serializers.ModelSerializer):
    class Meta:
        model = monitoring_services
        fields = ('id', 'sonata_srv_id', 'name', 'description', 'created')
        lookup_field = 'sonata_srv_id'

class SntFunctionsFullSerializer(serializers.ModelSerializer):
    #service = serializers.PrimaryKeyRelatedField(read_only=False, queryset=monitoring_services.objects.all())
    service = SntServicesSerializer()
    class Meta:
        model = monitoring_functions
        fields = ('id', 'sonata_func_id', 'name', 'description', 'created', 'service', 'host_id', 'pop_id')

class SntMetricsSerializer(serializers.ModelSerializer):
    #function = serializers.PrimaryKeyRelatedField(read_only=False, queryset=monitoring_functions.objects.all())
    #function = SntFunctionsSerializer()
    class Meta:
        model = monitoring_metrics
        fields = ('id', 'name', 'description', 'threshold', 'interval','cmd', 'function', 'created',)

class SntNewMetricsSerializer(serializers.ModelSerializer):
    #function = serializers.PrimaryKeyRelatedField(read_only=False, queryset=monitoring_functions.objects.all())
    #function = SntFunctionsSerializer()
    class Meta:
        model = monitoring_metrics
        fields = ('name', 'description', 'threshold', 'interval','cmd', 'function', 'created')

class SntMetricsFullSerializer(serializers.ModelSerializer):
    #function = serializers.PrimaryKeyRelatedField(read_only=False, queryset=monitoring_functions.objects.all())
    function = SntFunctionsSerializer()
    class Meta:
        model = monitoring_metrics
        fields = ('id', 'name', 'description', 'threshold', 'interval','cmd', 'function', 'created',)

class SntMetricsSerializer1(serializers.ModelSerializer):
    sonata_func_id = serializers.PrimaryKeyRelatedField(read_only=False, queryset=monitoring_functions.objects.all())

    class Meta:
        model = monitoring_metrics
        fields = ('id', 'name', 'description', 'threshold', 'interval','cmd', 'sonata_func_id', 'created',)

class SntNotifTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = monitoring_notif_types
        fields = ('id', 'type',)

class SntServicesLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = monitoring_services
        fields = ('sonata_srv_id', 'name')
        lookup_field = 'sonata_srv_id'

class SntRulesSerializer(serializers.ModelSerializer):
    #service = serializers.PrimaryKeyRelatedField(read_only=False, queryset=monitoring_services.objects.all()) 
    #notification_type = serializers.PrimaryKeyRelatedField(read_only=False, queryset=monitoring_notif_types.objects.all())
    service = SntServicesLightSerializer()
    notification_type = SntNotifTypeSerializer()
    class Meta:
        model = monitoring_rules
        fields = ('id', 'name', 'duration', 'summary', 'description', 'condition', 'notification_type','service', 'created',)
        lookup_field = 'consumer'


class SntRulesPerSrvSerializer(serializers.ModelSerializer):
    notification_type = SntNotifTypeSerializer()
    class Meta:
        model = monitoring_rules
        fields = ('id','function','vdu', 'name', 'duration', 'summary', 'description', 'condition', 'notification_type', 'created',)

class SntNewFunctionsSerializer(serializers.ModelSerializer):
    #service = serializers.PrimaryKeyRelatedField(read_only=False, queryset=monitoring_services.objects.all())
    #service = SntServicesSerializer()
    metrics = SntNewMetricsSerializer(many=True)
    class Meta:
        model = monitoring_functions
        fields = ('sonata_func_id', 'name', 'description', 'created', 'host_id', 'pop_id', 'metrics')

class LightFunctionsSerializer(serializers.ModelSerializer):
    vnfr_id = serializers.CharField(source='sonata_func_id')
    vc_id = serializers.CharField(source='host_id')
    vim_id = serializers.CharField()
    vim_endpoint = serializers.CharField(source='pop_id')
    class Meta:
        model = monitoring_functions
        fields = ('vnfr_id','vc_id', 'vim_id', 'vim_endpoint')

class SntNewRulesSerializer(serializers.ModelSerializer):
    #service = serializers.PrimaryKeyRelatedField(read_only=False, queryset=monitoring_services.objects.all())
    #function = serializers.PrimaryKeyRelatedField(read_only=False, queryset=monitoring_functions.objects.all())
    #notification_type = serializers.PrimaryKeyRelatedField(read_only=False, queryset=monitoring_notif_types.objects.all())
    class Meta:
        model = monitoring_rules
        fields = ('name', 'duration', 'summary', 'description', 'condition', 'notification_type', 'created',)

class NewServiceSerializer(serializers.Serializer):
    service = SntServicesSerializer()
    functions = SntNewFunctionsSerializer(many=True)
    rules = SntNewRulesSerializer(many=True)

class LightServiceSerializer(serializers.Serializer):
    ns_instance_uuid = serializers.CharField()
    test_id = serializers.CharField()
    functions = LightFunctionsSerializer(many=True)

class promMetricLabelSerializer(serializers.Serializer):
    metric_name = ''

class promMetricsListSerializer(serializers.Serializer):
    metrics = promMetricLabelSerializer(many=True)

class promLabelsSerializer(serializers.Serializer):
    labels = {'label':'id'}

class SntPromMetricSerializer(serializers.Serializer):
    name = serializers.CharField()
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    labels = promLabelsSerializer(many=True)
    step = serializers.CharField()

class CommentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    content = SntRulesSerializer(many=True)
    created = serializers.DateTimeField()

class wsLabelSerializer(serializers.Serializer):
    label = ''

class SntWSreqSerializer(serializers.Serializer):
    metric = serializers.CharField()
    filters = wsLabelSerializer(many=True)

class SntSPSerializer(serializers.ModelSerializer):
    class Meta:
        model = monitoring_service_platforms
        fields = ('id', 'sonata_sp_id', 'name', 'manager_url','created')

class SntPOPSerializer(serializers.ModelSerializer):
    class Meta:
        model = monitoring_pops
        fields = ('id', 'sonata_pop_id','sonata_sp_id' ,'name', 'prom_url','created')

class SntRulesConfSerializer(serializers.Serializer):
    rules = SntRulesPerSrvSerializer(many=True)

class SntActMonResSerializer(serializers.ModelSerializer):
    class Meta:
        model = active_monitoring_res
        fields = ('test_id', 'service_id', 'timestamp', 'config')

class SntActMonResDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = active_monitoring_res
        fields = ('service_id','timestamp','data')

class SntActMonResDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = active_monitoring_res
        fields = ('id', 'data')


class SntRulesFSerializer(serializers.ModelSerializer):
    notification_type = SntNotifTypeSerializer()

    class Meta:
        model = monitoring_rules
        fields = (
        'id', 'name', 'duration', 'summary', 'description', 'condition', 'notification_type', 'service', 'created',)


class SntRulesVduSerializer(serializers.Serializer):
    vdu_id = serializers.CharField()
    rules = SntRulesFSerializer(many=True)


class SntRulesVnfSerializer(serializers.Serializer):
    vnf_id = serializers.CharField()
    vdus = SntRulesVduSerializer(many=True)


class SntPLCRulesConfSerializer(serializers.Serializer):
    plc_contract = serializers.CharField()
    vnfs = SntRulesVnfSerializer(many=True)

    class Meta:
        fields = ('service_id', 'plc_contract','rules')

class SntSLARulesConfSerializer(serializers.Serializer):
    sla_contract = serializers.CharField()
    rules = SntRulesVnfSerializer(many=True)

    class Meta:
        fields = ('service_id', 'sla_contract','rules')


class CommentSerializer(serializers.Serializer):

    email = serializers.EmailField()
    content = serializers.CharField(max_length=200)
    created = serializers.DateTimeField()

    class Meta:
        fields = ('email', 'content')

class HealthSerializer (serializers.Serializer):
    alive_since = serializers.DateTimeField()

    class Meta:
        fields = ('alive_since')

class SntAlertsSerializer(serializers.Serializer):
    alertname = serializers.CharField()
    topic = serializers.CharField()
    serviceID = serializers.CharField()
    functionID = serializers.CharField()
    resource_id = serializers.CharField()
    alertstate = serializers.CharField()

class SntPromTargetUrlsSerializer(serializers.Serializer):
    MANO_TYPES = (
        ('osm', 'osm'),
        ('sonata', 'sonata'),
        ('onap', 'onap'),
    )
    sp_ip = serializers.CharField()
    type = serializers.ChoiceField(choices=MANO_TYPES)
    sp_name = serializers.CharField()
    targets = serializers.ListField(child=serializers.CharField(max_length=32, allow_blank=True))

class SntAlertsListSerializer(serializers.Serializer):
    status = serializers.CharField()
    alerts = SntAlertsSerializer(many=True)

class SntPromTargetSerializer(serializers.Serializer):
    targets=SntPromTargetUrlsSerializer(many=True)

class SntPromUrlsSerializer(serializers.Serializer):
    targets = serializers.ListField(child=serializers.CharField(max_length=32, allow_blank=True))

class SntPromTargetsSerializer(serializers.Serializer):
    static_configs = SntPromUrlsSerializer(many=True)
    job_name = serializers.CharField()

class SntPromConfSerializer(serializers.Serializer):
    config = serializers.CharField()

class SntPromConfSerialazer (serializers.Serializer):
    targets = serializers.JSONField

class SntPromTargetListSerializer(serializers.Serializer):
    targets=SntPromTargetsSerializer(many=True)