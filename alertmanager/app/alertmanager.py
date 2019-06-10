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

from flask import Flask, json, request
from rabbitMQ import amqp
from logger import TangoLogger as TangoLogger
import os, logging, datetime

app = Flask(__name__)
LOG = TangoLogger.getLogger(__name__, log_level=logging.INFO, log_json=True)
TangoLogger.getLogger("Alert_manager", logging.INFO, log_json=True)
LOG.setLevel(logging.INFO)
LOG.info('Alert manager to RMQ started ')

@app.before_first_request
def _declareStuff():
    global host
    global port
    global debug

    try:
        if 'RABBIT_URL' in os.environ:
            rabbit = str(os.environ['RABBIT_URL']).strip()
            global host
            global port
            host = rabbit.split(':')[0]
            port = int(rabbit.split(':')[1])
        else:
            raise ValueError('Rabbimq url unset')
    except ValueError as err:
        LOG.error("ValueError")
        return

    LOG.info('First message arrived')


@app.route("/")
def hello():
    urls =  "I am alive..."
    return urls

@app.route('/', methods = ['POST'])
def api():
    notif = json.loads(request.data)
    if 'alerts' in notif:
        for alert in notif['alerts']:
            msg = {}
            msg = alert['labels']
            msg['status'] =  alert['status']
            msg['startsAt'] = alert['startsAt']
            print(msg)
            type = 'undefined tp'
            topic = 'son.monitoring'
            if 'tp' in msg:
                if msg['tp'] == 'DEV':
                    type = 'dev'
                    topic = 'son.monitoring'
                else:
                    type = msg['tp']
                    topic = 'son.monitoring.' + msg['tp']
            rmq = amqp(host, port, topic, 'guest', 'guest')
            rmq.send(json.dumps(msg))
    LOG.debug("Notification Received "+ str(notif))
    return('', 204)




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
