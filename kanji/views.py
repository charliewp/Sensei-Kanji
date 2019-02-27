from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from django.urls import resolve
import pytz

import operator
import json
import random

from django import forms
from django.db import models
from datetime import datetime
from random import sample, randint
from django.db import IntegrityError, DataError
from django.conf import settings
#from django.conf import settings as djangoSettings

from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth import authenticate

from .models import EventLog
from .models import PingLog
from .models import Node
from .models import EventType
from .models import SensorType

import logging
log = logging.getLogger('KANJI-LOGGER')

from django.views.decorators.csrf import ensure_csrf_cookie
@ensure_csrf_cookie



# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the Sensei-Kanji index page.")
    
def node(request):
    if request.method == 'GET':
        #coreid = request.GET.get('coreid')
        url = request.path_info
        print("url={0}".format(url))
        pathParts = url.split("/")
        coreid = pathParts[len(pathParts)-1]
        print("coreId={0}".format(coreid))
        
        chartdefs = { "charts": [
                {
                    "title"     : "Temperature",
                    "ylabel"    : "Degrees F",
                    "yshow"     : "true",
                    "linecolor" : "red",
                    "ranges"    : [0, 45, 45, 85, 85, 110],
                    "fills"     : ['#0b2e7d 0.4', '#009900 0.4', '#dd2c00 0.4'],
                    "units"     : "F"
                },
                {
                    "title"     : "Network",
                    "ylabel"    : "millis",
                    "yshow"     : "true",
                    "linecolor" : "blue",
                    "ranges"    : [0, 250, 250, 750, 750, 1000],
                    "fills"     :  ['#ffe500 0.4', '#ffe500 0.4', '#dd2c00 0.4'],
                    "units"     : "ms"
                },
                {
                    "title"     : "Ping",
                    "ylabel"    : "ping",
                    "yshow"     : "true",
                    "linecolor" : "green",
                    "ranges"    : [0, 25, 25, 50, 50, 100],
                    "fills"     : ['#ffe500 0.4', '#ffe500 0.4', '#dd2c00 0.4'],
                    "units"     : "1/0"
                }
                
            ]
        }
        
        print("chardefs len={0}".format(len(chartdefs['charts'])))
        
        #print("name={0}".format(charts['charts'][1]['title']))
        
        series = []
        series.append(str("Temperature"))
        series.append("Network")
        series.append("Ping")
        
        #yaxis_labels = []
        #yaxis_labels.append("Degree F")
        #yaxis_labels.append("msecs")
        #yaxis_labels.append("ping")
        
        #colors = ["red", "blue", "green", "black"]
        
        data = []    

        # for each chart ...
        #ranges = [ [0, 45, 45, 85, 85, 110], [0, 250, 250, 750, 750, 1000], [0, 25, 25, 50, 50, 100] ]
        #fills  = [ ['#0b2e7d 0.4', '#009900 0.4', '#dd2c00 0.4'], ['#ffe500 0.4', '#ffe500 0.4', '#dd2c00 0.4'], ['#ffe500 0.4', '#ffe500 0.4', '#dd2c00 0.4']]
        #units = ["F", "ms", "UP"]
           
        node = Node.objects.all().filter(coreid=coreid).first()
        
        now = datetime.today()
        #now = timezone.now()
        time24hoursago = now - timedelta(hours=24)
        
        log.debug(time24hoursago)
        
        # get last 24hours       
        eventLogs = EventLog.objects.all().filter(node=node).filter(sensortype_id=7).filter(timestamp__gte = time24hoursago).order_by('timestamp')
        # get ALL
        #eventLogs = EventLog.objects.all().filter(node=node).filter(sensortype_id=7).order_by('timestamp')
        
        for eventLog in eventLogs:
            date_time = eventLog.timestamp.strftime("%m/%d/%Y %H:%M:%S")
            #date_time = eventLog.timestamp.strftime("%H:%M")
            #date_time = eventLog.timestamp.replace(tzinfo=timezone.utc).astimezone(tz="US/Eastern").strftime("%H:%M")
            ackTime = eventLog.meshacktimemillis
            pingLog = PingLog.objects.all().filter(node=node).filter(timestamp__gte = eventLog.timestamp).first()
            if ackTime>1000:
                ackTime=1000
            data.append([date_time, float(eventLog.eventdata), ackTime, pingLog.pingstate.idonlinestate])
        
        #ping = []
        
        #pingLogs = PingLog.objects.all().filter(node=node).filter(timestamp__gte = time24hoursago).order_by('timestamp')
        
        #for pingLog in pingLogs:        
        #    date_time = pingLog.timestamp.strftime("%m/%d/%Y %H:%M:%S")
        #    pingState = 100*(10001 - pingLog.pingstate.idonlinestate)
        #    ping.append([date_time, pingState])
        
        location = "{0}  Node:{1}".format(node.location.description, node.name)
        
        
        return render(request, 'node.html',  {'chartdefs': chartdefs, 'location': location, 'data': data, 'series': series })
          
def webhook(request):
   #
   # /kanji/webhooks will bring you here
   # this is for posting data only from the Particle Cloud
    
   # get the data and put it in the Database
   #content = request.get_json()
   #event = content['event']
   #data = content['data']
   #coreid = content['coreid']
   #published_at = content['published_at']
   str_content = request.body.decode("utf-8")
   print(str_content)
   json_data = json.loads(str_content.replace("'",'"'))
   
   event = json_data['event']
   data = json_data['data']
   coreid = json_data['coreid']
   published_at = json_data['published_at']
   timestamp = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%S.%fZ')
    
   dataParts = data.split("/")
    
   sensorid = dataParts[2]
   eventtype = dataParts[3]
   doc = dataParts[4]
   acktime = dataParts[5]

   print("iddevice={0}".format(coreid))
   print("publishtopic={0}".format(eventtype))
   print("sensorid={0}".format(sensorid))
   print("doc={0}".format(doc))
    
   # query = "INSERT INTO sensordb_event (timestamp, device_id, publishtopic_id, sensortype_id, doc, ack_time) \
   #      VALUES ('{0}', {1}, {2}, {3}, '{4}', {5})"\
   #      .format(dt.now(), iddevice, publishtopic, sensorid, doc, acktime)

   eventlog = EventLog()
   eventlog.timestamp = timestamp
   eventlog.node = Node.objects.all().filter(coreid=coreid).first()
   eventlog.eventtype = EventType.objects.get(pk=int(dataParts[3]))
   eventlog.sensortype = SensorType.objects.get(pk=int(dataParts[2]))
   eventlog.eventdata = doc
   eventlog.meshacktimemillis = int(acktime)  
   
   eventlog.save()
   
   return HttpResponse("Thanks, Sensei/Kanji")