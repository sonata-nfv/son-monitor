from django.core.management.base import BaseCommand
from django.utils import timezone
from api.management.commands.sonata import rabbitMQ
import threading


class creationConsumer (threading.Thread):
   def __init__(self, threadID, name, creds):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.creds = creds
      self.name = name

   def run(self):
      print ("Starting " + self.name)
      rmq = rabbitMQ.amqp(host=self.creds['host'], port=self.creds['port'], usr=self.creds['usr'], password=self.creds['password'])
      rmq.bind(topic='son-kernel', queue='mon.service.create', key='service.instances.create')
      rmq.consumer(queue='mon.service.create')
      print ("Exiting " + self.name)

class terminationConsumer (threading.Thread):
   def __init__(self, threadID, name, creds):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.creds = creds

   def run(self):
      print ("Starting " + self.name)
      rmq = rabbitMQ.amqp(host=self.creds['host'], port=self.creds['port'], usr=self.creds['usr'],
                          password=self.creds['password'])
      rmq.bind(topic='son-kernel', queue='mon.service.terminate', key='service.instances.terminate')
      rmq.consumer(queue='mon.service.terminate')
      print ("Exiting " + self.name)

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        creds = {}
        creds['host'] = '192.168.1.127'
        #creds['host'] = 'int-sp-ath.5gtango.eu'
        creds['port'] = 5672
        creds['usr'] = 'guest'
        creds['password'] = 'guest'
        thread1 = creationConsumer(1, "creationConsumer",creds)
        thread2 = terminationConsumer(2, "terminationConsumer", creds)
        thread1.start()
        thread2.start()

        while 1:
            pass

