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

from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from api import views, views_v2
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Monitoring Manager API",
      default_version='v2.5',
      description="Monitoring Manager API",
      terms_of_service="",
      contact=openapi.Contact(email="pkarkazis@synelixis.com"),
      license=openapi.License(name="Apache 2.0"),
   ),
   public=True,
   #permission_classes=(permissions.AllowAny,),
)

# API endpoints
urlpatterns2 = [
    
    url(r'^api/v1/users$', views.SntUsersList.as_view()),
	url(r'^api/v1/users/(?P<pk>[0-9]+)/$', views.SntUsersDetail.as_view()),
	url(r'^api/v1/users/type/(?P<type>[^/]+)/$', views.SntUserPerTypeList.as_view()),
	url(r'^api/v1/user/(?P<pk>[0-9]+)/$', views.SntUserList.as_view()),
	url(r'^api/v1/services$', views.SntServicesList.as_view()),
	url(r'^api/v1/services/user/(?P<usrID>[^/]+)/$', views.SntServicesPerUserList.as_view()),
    url(r'^api/v1/services/(?P<sonata_srv_id>[^/]+)/$', views.SntServicesDetail.as_view()),
	url(r'^api/v1/service/new$', views.SntNewServiceConf.as_view()),
	url(r'^api/v1/service/(?P<srvID>[^/]+)/$', views.SntServiceList.as_view()),
    #url(r'^api/v1/serviceconf$', views.SntServiceConfList.as_view()),

	url(r'^api/v1/functions$', views.SntFunctionsList.as_view()),
	#url(r'^api/v1/functions/(?P<pk>[0-9]+)/$', views.SntFunctionsDetail.as_view()),
	url(r'^api/v1/functions/service/(?P<srvID>[^/]+)/$', views.SntFunctionsPerServiceList.as_view()),

	url(r'^api/v1/metrics$', views.SntMetricsList.as_view()),
	#url(r'^api/v1/metrics/(?P<pk>[0-9]+)/$', views.SntMetricsDetail.as_view()),
	url(r'^api/v1/metrics/function/(?P<funcID>[^/]+)/$', views.SntMetricsPerFunctionList.as_view()),

	url(r'^api/v1/rules$', views.SntRulesList.as_view()),
	url(r'^api/v1/rules/service/(?P<srvID>[^/]+)/$', views.SntRulesPerServiceList.as_view()),
	url(r'^api/v1/rules/service/(?P<srvID>[^/]+)/configuration$', views.SntRuleconf.as_view()),
	url(r'^api/v1/rule/(?P<sonata_srv_id>[^/]+)/$', views.SntRulesDetail.as_view()),

	url(r'^api/v1/slamng/rules$', views.SntSLARulesList.as_view()),
	url(r'^api/v1/slamng/rules/service/(?P<srvID>[^/]+)/$', views.SntSLARulesPerServiceList.as_view()),
	url(r'^api/v1/slamng/rules/service/(?P<srvID>[^/]+)/configuration$', views.SntSLARuleconf.as_view()),
	url(r'^api/v1/slamng/rule/(?P<sonata_srv_id>[^/]+)/$', views.SntSLARulesDetail.as_view()),

	url(r'^api/v1/policymng/rules$', views.SntPLCRulesList.as_view()),
	url(r'^api/v1/policymng/rules/service/(?P<srvID>[^/]+)/$', views.SntPLCRulesPerServiceList.as_view()),
	url(r'^api/v1/policymng/rules/service/(?P<srvID>[^/]+)/configuration$', views.SntPLCRuleconf.as_view()),
	url(r'^api/v1/policymng/rule/(?P<sonata_srv_id>[^/]+)/$', views.SntPLCRulesDetail.as_view()),

	url(r'^api/v1/notification/types$', views.SntNotifTypesList.as_view()),
	url(r'^api/v1/notification/type/(?P<pk>[0-9]+)/$', views.SntNotifTypesDetail.as_view()),
	url(r'^api/v1/notification/smtp/component/(?P<component>[^/]+)/$', views.SntSmtpList.as_view()),
	url(r'^api/v1/notification/smtp$', views.SntSmtpCreate.as_view()),
	url(r'^api/v1/notification/smtp/(?P<pk>[0-9]+)/$', views.SntSmtpDetail.as_view()),

	url(r'^api/v1/pop$', views.SntPOPList.as_view()),
	url(r'^api/v1/pop/splatform/(?P<spID>[^/]+)/$', views.SntPOPperSPList.as_view()),
	url(r'^api/v1/pop/(?P<sonata_pop_id>[^/]+)/$', views.SntPOPDetail.as_view()),			#karpa

	url(r'^api/v1/splatform$', views.SntSPList.as_view()),
	url(r'^api/v1/splatform/(?P<pk>[0-9]+)/$', views.SntSPDetail.as_view()),

	url(r'^api/v1/prometheus/metrics/list$', views.SntPromMetricList.as_view()),
	url(r'^api/v1/prometheus/vnf/(?P<vnf_id>[^/]+)/metrics/list$', views.SntPromMetricListVnf.as_view()),
    url(r'^api/v1/prometheus/vnf/(?P<vnf_id>[^/]+)/vdu/(?P<vdu_id>[^/]+)/metrics/list$', views.SntPromMetricListVnfVdu.as_view()),
	url(r'^api/v1/prometheus/metrics/name/(?P<metricName>[^/]+)/$', views.SntPromMetricDetail.as_view()),
    url(r'^api/v1/prometheus/vnf/(?P<vnf_id>[^/]+)/metrics/name/(?P<metricName>[^/]+)/$', views.SntPromVnfMetricDetail.as_view()),
    url(r'^api/v1/prometheus/vnf/(?P<vnf_id>[^/]+)/vdu/(?P<vdu_id>[^/]+)/metrics/data$', views.SntPromMetricDataPerVnf.as_view()),
    url(r'^api/v1/prometheus/vnf/(?P<vnf_id>[^/]+)/metrics/data$', views.SntPromMetricDataPerVnf.as_view()),
	url(r'^api/v1/prometheus/metrics/data$', views.SntPromMetricData.as_view()),
	url(r'^api/v1/prometheus/configuration$', views.SntPromSrvConf.as_view()),

	url(r'^api/v1/prometheus/pop/(?P<popID>[^/]+)/metrics/list$', views.SntPromMetricPerPOPList.as_view()),
	url(r'^api/v1/prometheus/pop/(?P<popID>[^/]+)/metrics/name/(?P<metricName>[^/]+)/$', views.SntPromMetricPerPOPDetail.as_view()),
	url(r'^api/v1/prometheus/pop/(?P<popID>[^/]+)/metrics/data$', views.SntPromMetricPerPOPData.as_view()),
	url(r'^api/v1/prometheus/pop/(?P<popID>[^/]+)/configuration$', views.SntPromSrvPerPOPConf.as_view()),

	url(r'^api/v1/ws/new$', views.SntWSreq.as_view()),
	url(r'^api/v1/ws/pop/(?P<popID>[^/]+)/new$', views.SntWSreqPerPOP.as_view()),	#karpa

    url(r'^api/v1/active/service/(?P<service_id>[^/]+)/test/list$', views.SntActMRList.as_view()),
    url(r'^api/v1/active/service/(?P<service_id>[^/]+)/test/(?P<test_id>[^/]+)/$', views.SntActMRDetail.as_view()),
    url(r'^api/v1/active/service/(?P<service_id>[^/]+)/test/(?P<test_id>[^/]+)/data$', views.SntActMRDt.as_view()),
    url(r'^api/v1/active/service/(?P<service_id>[^/]+)/test$', views.SntActMRDelete.as_view()),

	url(r'^api/v1/snmp/entities$', views.SntSNMPEntList.as_view()),
	url(r'^api/v1/snmp/entity$', views.SntSNMPEntCreate.as_view()),
	url(r'^api/v1/snmp/entity/(?P<pk>[0-9]+)/$', views.SntSNMPEntDetail.as_view()),
]

urlpatterns3 = [
	
	url(r'^api/v2/sla/monitoring-rules/service/(?P<srv_id>[^/]+)$', views_v2.SntSLARulesPerServiceList.as_view()),
	url(r'^api/v2/sla/monitoring-rules$', views_v2.SntSLARuleconf.as_view()),
	url(r'^api/v2/sla/monitoring-alerts$', views_v2.SntSLAAlertsList.as_view()),

	url(r'^api/v2/policies/monitoring-rules/service/(?P<srv_id>[^/]+)$', views_v2.SntPLCRulesPerServiceList.as_view()),
	url(r'^api/v2/policies/monitoring-rules$', views_v2.SntPLCRuleconf.as_view()),
	url(r'^api/v2/policies/monitoring-alerts$', views_v2.SntPLCAlertsList.as_view()),

	url(r'^api/v2/notification-types$', views_v2.SntNotifTypesList.as_view()),
	url(r'^api/v2/notification-types/(?P<pk>[0-9]+)$', views_v2.SntNotifTypesDetail.as_view()),

	url(r'^api/v2/pops$', views_v2.SntPOPList.as_view()),
	url(r'^api/v2/pops/(?P<pop_id>[^/]+)$', views_v2.SntPOPDetail.as_view()),

	url(r'^api/v2/services$', views_v2.SntNewServiceConf.as_view()),
	url(r'^api/v2/services/(?P<srv_id>[^/]+)$', views_v2.SntServicesDetail.as_view()),
    url(r'^api/v2/services/(?P<srv_id>[^/]+)/metrics$', views_v2.SntPromNSMetricListVnf.as_view()),
	url(r'^api/v2/vnfs/(?P<vnf_id>[^/]+)/metrics$', views_v2.SntPromMetricListVnf.as_view()),
	url(r'^api/v2/vnfs/(?P<vnf_id>[^/]+)/vdu/(?P<vdu_id>[^/]+)/metrics$',views_v2.SntPromMetricListVnfVdu.as_view()),

	url(r'^api/v2/prometheus/metrics$', views_v2.SntPromMetricList.as_view()),
	url(r'^api/v2/prometheus/targets$', views_v2.SntPromSrvTargets.as_view()),

	url(r'^api/v2/prometheus/metrics/name/(?P<metricName>[^/]+)$', views_v2.SntPromMetricDetail.as_view()),
	url(r'^api/v2/prometheus/configuration$', views_v2.SntPromSrvConf.as_view()),

	url(r'^api/v2/wss$', views_v2.SntWSreq.as_view()),

	url(r'^api/v2/active-monitoring-tests/service/(?P<srv_id>[^/]+)$', views_v2.SntActMRList.as_view()),
	url(r'^api/v2/active-monitoring-tests/service/(?P<srv_id>[^/]+)/test/(?P<test_id>[^/]+)$', views_v2.SntActMRDetail.as_view()),
	url(r'^api/v2/active-monitoring-tests$', views_v2.SntActMRPost.as_view()),

	url(r'^api/v2/snmps$', views_v2.SntSNMPEntCreate.as_view()),
	url(r'^api/v2/snmps/(?P<pk>[0-9]+)$', views_v2.SntSNMPEntDetail.as_view()),
]

urlpatterns4 = [
    url(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
	url(r'^pings$', views.Ping.as_view(), name='health'),
]

public_apis_v1 = format_suffix_patterns(urlpatterns2)
public_apis_v2 = format_suffix_patterns(urlpatterns3)
doc = format_suffix_patterns(urlpatterns4)

urlpatterns1 = [
    url(r'^pings$', views_v2.Ping.as_view()),
	url(r'^api/v2/internal/smtp/creds/(?P<component>[^/]+)$', views.SntCredList.as_view()),
]

internal_apis = format_suffix_patterns(urlpatterns1)