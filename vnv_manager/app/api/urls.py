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

from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi



schema_view = get_schema_view(
   openapi.Info(
      title="VnV Monitoring Manager API",
      default_version='v2.0',
      description="VnV Monitoring Manager API",
      terms_of_service="",
      contact=openapi.Contact(email="pkarkazis@synelixis.com"),
      license=openapi.License(name="Apache 2.0"),
   ),
   public=True,
   #permission_classes=(permissions.AllowAny,),
)


# API endpoints
urlpatterns1 = [
	url(r'^api/v1/internal/smtp/creds/(?P<component>[^/]+)$', views.SntCredList.as_view()),

]


urlpatterns2 = [
    url(r'^sla/monitoring-rules/service/(?P<srv_id>[^/]+)$', views.SntSLARulesPerServiceList.as_view()),
	url(r'^sla/monitoring-rules$', views.SntSLARuleconf.as_view()),
	url(r'^sla/monitoring-alerts$', views.SntSLAAlertsList.as_view()),

	url(r'^policies/monitoring-rules/service/(?P<srv_id>[^/]+)$', views.SntPLCRulesPerServiceList.as_view()),
	url(r'^policies/monitoring-rules$', views.SntPLCRuleconf.as_view()),
	url(r'^policies/monitoring-alerts$', views.SntPLCAlertsList.as_view()),

	#url(r'^notification-types$', views.SntNotifTypesList.as_view()),
	#url(r'^notification-types/(?P<pk>[0-9]+)$', views.SntNotifTypesDetail.as_view()),

	url(r'^services$', views.SntNewService.as_view()),
	url(r'^services/(?P<srv_id>[^/]+)$', views.SntServicesDetail.as_view()),
    url(r'^services/(?P<srv_id>[^/]+)/metrics$', views.SntPromNSMetricListVnf.as_view()),
	url(r'^vnfs/(?P<vnf_id>[^/]+)/metrics$', views.SntPromMetricListVnf.as_view()),
	url(r'^vnfs/(?P<vnf_id>[^/]+)/vdu/(?P<vdu_id>[^/]+)/metrics$',views.SntPromMetricListVnfVdu.as_view()),

	url(r'^prometheus/metrics$', views.SntPromMetricList.as_view()),
	url(r'^prometheus/metrics/name/(?P<metricName>[^/]+)$', views.SntPromMetricDetail.as_view()),
	url(r'^prometheus/configuration$', views.SntPromSrvConf.as_view()),

	url(r'^active-monitoring-tests/service/(?P<srv_id>[^/]+)$', views.SntActMRList.as_view()),
	url(r'^active-monitoring-tests/service/(?P<srv_id>[^/]+)/test/(?P<test_id>[^/]+)$', views.SntActMRDetail.as_view()),
	url(r'^active-monitoring-tests$', views.SntActMRPost.as_view()),

	#url(r'^snmps$', views.SntSNMPEntCreate.as_view()),
	#url(r'^snmps/(?P<pk>[0-9]+)$', views.SntSNMPEntDetail.as_view()),
]

urlpatterns3 = [
    #url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
	url(r'^pings$', views.Ping.as_view(), name='health'),
]

doc = format_suffix_patterns(urlpatterns3)
public_apis = format_suffix_patterns(urlpatterns2)
internal_apis = format_suffix_patterns(urlpatterns1)


	