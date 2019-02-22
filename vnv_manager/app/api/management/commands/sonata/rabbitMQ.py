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

import pika, yaml
from pika import exceptions
from api.management.commands.sonata.sonata import Sonata

class amqp(object):

    def __init__(self, host, port, usr, password):
        self.host = host
        self.port = port
        self.credentials = pika.PlainCredentials(usr, password)

    def send(self,topic, key, msg):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(self.host, self.port, '/', self.credentials))
        except pika.exceptions.AMQPError as error:
            print(error)
            return
        channel = connection.channel()
        channel.basic_publish(exchange='son-kernel', routing_key=key, body=msg)
        connection.close()

    def bind(self,topic,queue,key):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(self.host, self.port, '/', self.credentials))
        except pika.exceptions.AMQPError as error:
            print(error)
            return
        channel = connection.channel()
        channel.queue_declare(queue=queue)
        channel.queue_bind(exchange=topic, queue=queue, routing_key=key)
        connection.close()

    def consumer(self,queue):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(self.host, self.port, '/', self.credentials))
        except pika.exceptions.AMQPError as error:
            print(error)
            return
        channel = connection.channel()
        channel.queue_declare(queue=queue)

        def callback(ch, method, properties, body):
            if queue == 'mon.service.create':
                try:
                    msg = yaml.load(body)
                    if 'NSD' in msg:
                        Sonata().ns_descriptor(msg)
                    elif 'nsr' in msg:
                        if msg['error'] == None and msg['status'] == 'READY':
                            Sonata().ns_records(msg)
                except yaml.YAMLError as exc:
                    print(exc)
                    print(" [x] Received %r" % (body,))
            elif queue == 'mon.service.terminate':
                try:
                    msg = yaml.load(body)
                    Sonata().ns_termination(msg)
                except yaml.YAMLError as exc:
                    print(exc)
                    print(" [x] Received %r" % (body,))

        channel.basic_consume(callback,
                              queue=queue,
                              no_ack=True)

        channel.start_consuming()


if __name__ == '__main__':
    rmq = amqp(host='192.168.1.127', port=5672, usr='guest', password='guest')
    rmq.bind(topic='son-kernel',queue='mon.service.create',key='service.instances.create')
    #rmq.bind(topic='son-kernel', queue='mon.service.terminate', key='service.instances.terminate')
    rmq.send(topic='son-kernel',key='service.instances.create',msg='lalakis')
    #rmq.consumer(queue='mon.service.create')

