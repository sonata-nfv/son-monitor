'''
Copyright (c) 2015 SONATA-NFV [, ANY ADDITIONAL AFFILIATION]
ALL RIGHTS RESERVED.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Neither the name of the SONATA-NFV [, ANY ADDITIONAL AFFILIATION]
nor the names of its contributors may be used to endorse or promote 
products derived from this software without specific prior written 
permission.

This work has been performed in the framework of the SONATA project,
funded by the European Commission under Grant number 671517 through 
the Horizon 2020 and 5G-PPP programmes. The authors would like to 
acknowledge the contributions of their colleagues of the SONATA 
partner consortium (www.sonata-nfv.eu).
'''

import json
import httplib2

class Http(object):
    def __init__(self,logger):
        self.LOG =logger
        
    def GET(self,url_,headers_):
        try:
            httpServ = httplib2.Http()
            response, content = httpServ.request(url_,headers={'Content-Type':'application/json'} ,method='GET')
            if response.status == 200:
                data = json.loads(content.decode())
            else:
                data = {'response_status': response.status}
            return data
        
        except httplib2.HttpLib2Error as e:
            self.LOG.info('HttpLib2Error')
            return str(e)
        except httplib2.ServerNotFoundError as e:
            self.LOG.info('ServerNotFoundError')
            return (e)
        except ValueError as e:
            self.LOG.info('ValueError')
            return (e)

    def POST(self, url_,headers_,data_):
        try:
            httpServ = httplib2.Http()
            response, content = httpServ.request(url_, headers={'Content-Type':'application/json'},
                                        body=data_,
                                        method='POST')

            return response.status
        except httplib2.HttpLib2Error as e:
            self.LOG.info('HttpLib2Error')
            return str(e)
        except httplib2.ServerNotFoundError as e:
            self.LOG.info('ServerNotFoundError')
            return (e)
        except ValueError as e:
            self.LOG.info('ValueError')
            return (e)

    def DELETE(self, url_,headers_):
        try:
            httpServ = httplib2.Http()
            response, content = httpServ.request(url_, headers={'Content-Type': 'text/html'},
                                                 method='DELETE')
            return response.status

        except httplib2.HttpLib2Error as e:
            self.LOG.info('HttpLib2Error')
            return str(e)
        except httplib2.ServerNotFoundError as e:
            self.LOG.info('ServerNotFoundError')
            return (e)
        except ValueError as e:
            self.LOG.info('ValueError')
            return (e)
