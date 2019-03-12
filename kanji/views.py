from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from django.urls import resolve
import pytz

import operator
import json
import random
import html

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
from .models import MeshNetwork
from .models import Channel

import logging
log = logging.getLogger('KANJI-LOGGER')

from django.views.decorators.csrf import ensure_csrf_cookie
@ensure_csrf_cookie

# Create your views here.

def chart(request):
    html = Template('{% load static %}<img src="{% static "channel.png" %}" />')
    return HttpResponse(html.render(Context(request)))
    
def index(request):
    return HttpResponse("Hello, world. You're at the Sensei-Kanji index page.")

    
def channel(request):
    #
    #  Here we are looking at events from all nodes on a meshchannel
    #  meshchannel = meshnetwork/channel
    #
    #  request url ~ /channel/meshnetwork_id/channel_id
    if request.method == 'GET':
        url = request.path_info
        #print("url={0}".format(url))
        pathParts = url.split("/")
        meshnetwork_id = int(pathParts[len(pathParts)-2])
        channel_id = int(pathParts[len(pathParts)-1])
        
        meshnetworkname = MeshNetwork.objects.get(pk=int(meshnetwork_id)).name
        channelname = Channel.objects.get(pk=int(channel_id)).name
        
        print("PRINT view/channel meshnetwork_id={0} channel_id={1}".format(meshnetwork_id, channel_id))
        log.info("INFO view/channel meshnetwork_id={0} channel_id={1}".format(meshnetwork_id, channel_id))
        log.error("ERROR view/channel meshnetwork_id={0} channel_id={1}".format(meshnetwork_id, channel_id))
        
        chartdefs = { "charts": [] }
        
        now = datetime.today()
        time24hoursago = now - timedelta(hours=24)
        #log.debug(time24hoursago)
        
        # we'll get data from the NodeType = sensors 
        nodes = Node.objects.all().filter(meshnetwork_id=meshnetwork_id).filter(channel_id=channel_id).filter(nodetype_id=10000)
        
        data = []
        
        #eventMarkers.data([
        #    {date: '2001-09-11', description: '9-11 attacks'},
        #    {date: '2003-03-20', description: 'Iraq War'},
        #    {date: '2008-08-20', description: 'Global financial collapse'},
        #    {date: '2009-02-05', description: 'OPEC cuts production targets 4.2 mmbpd'},
        #    {date: '2009-11-15', description: 'Greece\'s debt crisis'},
        #    {date: '2011-03-11', description: 'Japan earthquake'},
        #    {date: '2014-12-01', description: 'Russian financial crisis'},
        #    {date: '2015-03-15', description: 'OPEC production quota unchanged'}
        #]);
        
        eventmarkers = {"groups": [{"format": "FAN", "width": "35", "height": "35", "fill": "#ff6a00", "data": [] },
                                   {"format": "FAN", "width": "35", "height": "35", "fill": "#00f700", "data": [] } ] }
        
        state = 0
        
        colors = ["red", "green", "blue"]
        
        nodenumber = 0
        for node in nodes:
            # get last 24hours       
            eventLogs = EventLog.objects.all().filter(node=node).filter(sensortype_id=7).filter(timestamp__gte = time24hoursago).order_by('timestamp')
            # eventLogs = EventLog.objects.all().filter(node=node).filter(sensortype_id=7).order_by('timestamp')
            nodedata = []
            for eventLog in eventLogs:
              eventtime = eventLog.timestamp
              #date_time = eventLog.timestamp.strftime("%m/%d/%Y %H:%M")
              date_time = eventLog.timestamp.strftime("%Y-%m-%d %H:%M")
              nodedata.append([date_time, float(eventLog.eventdata)])
              # synthetic controller input
              if nodenumber == 0:
                if state==0 and float(eventLog.eventdata)>75.0:
                  state = 1
                  eventmarker = {}
                  eventmarker['date'] = date_time
                  eventmarker['description'] = "Fans On"
                  eventmarkers['groups'][0]['data'].append(eventmarker)
                elif state==1 and float(eventLog.eventdata)<73.8:
                  state = 0
                  eventmarker = {}
                  eventmarker['date'] = date_time
                  eventmarker['description'] = "Fans Off"
                  eventmarkers['groups'][1]['data'].append(eventmarker)
            #print("node {0} data ={1}".format(node.name, nodedata))  
            data.append(nodedata)
                        
            chartdef = {
                    "title"     : node.name,
                    "ylabel"    : node.name,
                    "yshow"     : "false",
                    "linecolor" : colors[nodenumber],
                    "ranges"    : [0, 25, 25, 50, 50, 100],
                    "fills"     : ['#ffe500 0.4', '#ffe500 0.4', '#dd2c00 0.4'],
                    "units"     : "1/0",
                    "gaugeshow" : "false",
                    "gaugefont" : "44",
                    "gaugexoff" : "20%",
                    "gaugeyoff" : "20%"
            }
            #print("chartdef ={0}".format(chartdef))
            chartdefs['charts'].append(chartdef)
            nodenumber = nodenumber + 1
        
        #print("chartdefs ={0}".format(chartdefs))
        #log.error("channel data ={0}".format(data[1]))
        log.error("eventmarkers ={0}".format(eventmarkers))
        td = timezone.now() - eventtime       
        timediffstr = str(td.days) + "d " + str(td.seconds // 3600) + "h " + str(td.seconds // 60 % 60) + "m " + str(td.seconds % 60) + "s ago"
        location = "mesh {0}/{1} channel".format(meshnetworkname, channelname)
        
        return render(request, 'channel.html',  {'charttitle': 'Channel History', 'location': location, 'chartdefs': chartdefs, 'data': data, 'eventmarkers': eventmarkers })
          
    
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
                    "units"     : "F",
                    "gaugeshow" : "true",
                    "gaugefont" : "44",
                    "gaugexoff" : "50%",
                    "gaugeyoff" : "20%"
                    
                },
                {
                    "title"     : "Network",
                    "ylabel"    : "millis",
                    "yshow"     : "true",
                    "linecolor" : "blue",
                    "ranges"    : [0, 250, 250, 750, 750, 1000],
                    "fills"     :  ['#ffe500 0.4', '#ffe500 0.4', '#dd2c00 0.4'],
                    "units"     : "ms",
                    "gaugeshow" : "true",
                    "gaugefont" : "24",
                    "gaugexoff" : "50%",
                    "gaugeyoff" : "20%"
                },
                {
                    "title"     : "Ping",
                    "ylabel"    : "ping",
                    "yshow"     : "false",
                    "linecolor" : "green",
                    "ranges"    : [0, 25, 25, 50, 50, 100],
                    "fills"     : ['#ffe500 0.4', '#ffe500 0.4', '#dd2c00 0.4'],
                    "units"     : "1/0",
                    "gaugeshow" : "false",
                    "gaugefont" : "44",
                    "gaugexoff" : "20%",
                    "gaugeyoff" : "20%"
                }
                
            ]
        }
        
              
        
           
        node = Node.objects.all().filter(coreid=coreid).first()
        now = datetime.today()
        time24hoursago = now - timedelta(hours=24)
        log.debug(time24hoursago)
        # get last 24hours       
        eventLogs = EventLog.objects.all().filter(node=node).filter(sensortype_id=7).filter(timestamp__gte = time24hoursago).order_by('timestamp')
        # eventLogs = EventLog.objects.all().filter(node=node).filter(sensortype_id=7).order_by('timestamp')
        
        data = []
        for eventLog in eventLogs:
            eventtime = eventLog.timestamp
            date_time = eventLog.timestamp.strftime("%m/%d/%Y %H:%M:%S")
            ackTime = eventLog.meshacktimemillis
            pingLog = PingLog.objects.all().filter(node=node).filter(timestamp__gte = eventLog.timestamp).first()
            
            if ackTime>1000:
                ackTime=1000
            
            if pingLog:
                data.append([date_time, float(eventLog.eventdata), ackTime, pingLog.pingstate.idonlinestate])
            else:
                data.append([date_time, float(eventLog.eventdata), ackTime, 500])
        
        td = timezone.now() - eventtime       
        timediffstr = str(td.days) + "d " + str(td.seconds // 3600) + "h " + str(td.seconds // 60 % 60) + "m " + str(td.seconds % 60) + "s ago"
        location = "{0}  Node:{1}".format(node.location.description, node.name)
        
        return render(request, 'node.html',  {'location': location, 'timediff': timediffstr, 'chartdefs': chartdefs, 'data': data })
          
def webhook(request):
   #
   # /kanji/webhooks will bring you here
   # this is for posting data only from the Particle Cloud
    
   # get the data and put it in the Database
   #content = request.get_json()
   #event = content['event']
   #print("event={0}".format(event))
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
    
   #sensorid = dataParts[2]
   #eventtype = dataParts[3]
   #doc = dataParts[4]
   #acktime = dataParts[5]
   
   doc = dataParts[0]   
   acktime = dataParts[1]
   
   
   pins = json.loads(doc)   
   for pin in pins:
      log.error("ERROR view/webhook pin={0}".format(pin))
   
   eventtype = 10000
   sensorid = pin["t"]

       
   # query = "INSERT INTO sensordb_event (timestamp, device_id, publishtopic_id, sensortype_id, doc, ack_time) \
   #      VALUES ('{0}', {1}, {2}, {3}, '{4}', {5})"\
   #      .format(dt.now(), iddevice, publishtopic, sensorid, doc, acktime)

   eventlog = EventLog()
   eventlog.timestamp = timestamp
   eventlog.node = Node.objects.all().filter(coreid=coreid).first()
   eventlog.eventtype = EventType.objects.get(pk=eventtype)
   eventlog.sensortype = SensorType.objects.get(pk=sensorid)
   eventlog.eventdata = doc
   eventlog.meshacktimemillis = int(acktime)  
   
   eventlog.save()
   
   log.error("ERROR view/webhook data={0}".format(data))
   log.error("ERROR view/webhook ackTime={0}".format(acktime))
   log.error("ERROR view/webhook core={0}".format(eventlog.node.name))
   log.error("ERROR view/webhook iddevice={0}".format(coreid))
   log.error("ERROR view/webhook publishtopic={0}".format(eventtype))
   log.error("ERROR view/webhook sensorid={0}".format(sensorid))
   log.error("ERROR view/webhook doc={0}".format(doc))
   
   return HttpResponse("Thanks, Sensei/Kanji")