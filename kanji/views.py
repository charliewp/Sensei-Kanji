from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from django.urls import resolve
import pytz

import operator
import json
import random
import html
import wave

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
from .models import Urgency
from .models import Impact
from .models import User
from .models import SensorType
from .models import MeshNetwork
from .models import Channel

from django.template import RequestContext, Template, Context

from slackclient import SlackClient
import urllib
from urllib.parse import urlparse
import requests
import configparser

import logging
log = logging.getLogger('KANJI-LOGGER')

from django.views.decorators.csrf import ensure_csrf_cookie

    
@ensure_csrf_cookie

# Create your views here.
def index(request):
    url = request.path_info
    pathParts = url.split("/")
    customerid = int(pathParts[len(pathParts)-1])
    nodes = Node.objects.all().filter(deploystate_id=10001).filter(customer_id=customerid).order_by('name')
    networkstatus = []
    now = datetime.today()
    timestamp = now.strftime("%I:%M %p %A, %B %e, %Y")
    time24hoursago = now - timedelta(hours=24)
    nodecount = 0
    for node in nodes:
      nodestatus = {}
      totalPings  = PingLog.objects.all().filter(node=node).filter(timestamp__gte = time24hoursago).count()
      pingSuccess = PingLog.objects.all().filter(node=node).filter(timestamp__gte = time24hoursago).filter(pingstate_id=10000).count()
      pctVisible = 100.0 * float(pingSuccess/totalPings)
      nodecount += 1
      log.error("Node {0} is {1:.1f}%".format(node.name, pctVisible))
      nodestatus["name"] = node.name
      nodestatus["availpct"] = "{0:.1f}%".format(pctVisible)
      nodestatus["application"] = node.application.description
      networkstatus.append(nodestatus)
    return render(request, 'meshio.html', {"nodecount": nodecount, "networkstatus": networkstatus, "timestamp": timestamp, "customerid": customerid})
   

def squealer(request):
    url = request.path_info
    print(url)
    now = datetime.today()
    timehoursago = now - timedelta(hours=2)
    #timestamp = now.strftime("%I:%M %p %A, %B %e, %Y")
    squealevents = EventLog.objects.filter(sensortype_id=100).filter(timestamp__gte = timehoursago).order_by('-timestamp')
    squeals = []
    for squealevent in squealevents:
      eventdata = json.loads(squealevent.eventdata)
      filename = eventdata[0]['f']
      squeal = {}
      squeal['location'] = squealevent.node.location.description
      squeal['time'] = squealevent.timestamp
      squeal['tape'] = "squealtape_" + filename
      #squealevent.timestamp.strftime("%m%d%Y__%H%M%S") + ".wav"
      #print(squealevent.timestamp)
      squeals.append(squeal)
              
    return render(request, 'squealers.html', {'timestamp': now, 'squealers': squeals})   
    
def dashboard(request):
    # read data                                                                                                  
    print("dashboard view")
    url = request.path_info
    pathParts = url.split("/")
    print(pathParts)
    categories = ["A", "B", "C"]
    values = [1,2,3]
    
    table_content = []
    charttitle = "'Squeals'"
    chartseries = "'Squeals/hour'"
    chartunits = "'Squeals'"
	
    context = {"categories": categories, 'values': values, 'charttitle': charttitle, 'chartseries': chartseries, 'chartunits': chartunits, 'table_data': table_content}
    return render(request, 'dashboard.html', context=context)
    
def channel(request):
    #
    #  Here we are looking at events from all nodes on a meshchannel
    #  meshchannel = meshnetwork/channel
    #
    #  request url ~ /channel/meshnetwork_id/channel_id
    if request.method == 'GET':
        url = request.path_info
        print("image={0}".format(url))
        pathParts = url.split("/")
        image = pathParts[len(pathParts)-1]
        return render(request, 'channelchart.html', { 'image': image} )
    
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
        time24hoursago = now - timedelta(days=24)
        log.debug(time24hoursago)
        # get last 24hours       
        eventLogs = EventLog.objects.all().filter(node=node).filter(sensortype_id=7).filter(timestamp__gte = time24hoursago).order_by('timestamp')
        # eventLogs = EventLog.objects.all().filter(node=node).filter(sensortype_id=7).order_by('timestamp')
        
        eventtime = timezone.now()
        
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
      
def oldslack(request):
   #process POST requests from Slack when a user selects a button
   log.error("INFO view/slack has been called!")
   payload = request.body.decode("utf-8")
   payload = urllib.parse.parse_qs(payload)
   payload = json.loads(payload['payload'][0])
   log.error(payload)
   log.error("payload {0}".format(payload["actions"][0]))
   action = payload["actions"][0]
   log.error(action)
   
   actionname = action["value"]
   actiontarget = action["action_id"]
   
   #we lookup the coreid of the action target and call the function named in 'actionname'   
   device = Node.objects.get(pk=int(actiontarget))
   
   if device:
     now = datetime.now()
     timestamp = now.strftime("%I:%M %p %A, %B %e, %Y")
     _SLACK_TOKEN = device.location.customer.slacktoken
     slackchannel = device.location.slackchannel
     log.error("slackChannel={0} slackToken={1}".format(slackchannel,_SLACK_TOKEN))
   
     config = configparser.ConfigParser()
     config.read('secrets.conf')
        
     log.error("Calling {0} on coreid={1}".format(actionname,device.coreid))
   
     _PARTICLE_TOKEN = config['DEFAULT']['_PARTICLE_TOKEN']
     log.error("secrets _PARTICLE_TOKEN {0}".format(_PARTICLE_TOKEN))
   
     actionurl = "https://api.particle.io/v1/devices/{0}/{1}".format(device.coreid,actionname)
     log.error(actionurl)
     data = {'access_token' : _PARTICLE_TOKEN, 'arg' : ""}
     resp = requests.post(actionurl, data = data, timeout=(15, 30))
     response = resp.json()
     log.error("response={0}".format(response))
   
     log.error("secrets _SLACK_TOKEN {0}".format(_SLACK_TOKEN))    
   
     messagestring = "[\
       {\"type\": \"section\", \
		 \"text\": { \
			\"type\": \"mrkdwn\", \
			\"text\": \"*<fakeLink.toUserProfiles.com|Iris / Zelda 1-1>*\\nTuesday, January 21 4:00-4:30pm\\nBuilding 2 - Havarti Cheese (3)\\n2 guests\" \
		 }, \
		 \"accessory\": { \
			\"type\": \"image\", \
			\"image_url\": \"https://api.slack.com/img/blocks/bkb_template_images/notifications.png\", \
			\"alt_text\": \"calendar thumbnail\" \
		 } \
     }]"
    
     blockmessage = json.loads(messagestring)
   
     if response["return_value"] ==0:
       blockmessage[0]["accessory"]["image_url"] = "https://www.dropbox.com/s/2vvxy36e3jblulb/check.png?raw=1"
       blockmessage[0]["accessory"]["alt_text"] = "Ok thumbnail"
       blockmessage[0]["text"]["text"] = "*At {0} {1}*".format(timestamp, "The test was successful!")
     else:
       blockmessage[0]["accessory"]["image_url"] = "https://www.dropbox.com/s/lzgeet9bqqw1ftw/fail.png?raw=1"
       blockmessage[0]["accessory"]["alt_text"] = "Failed thumbnail"
       blockmessage[0]["text"]["text"] = "*At {0} {1}*".format(timestamp, "The test failed.")

   
     sc = SlackClient(_SLACK_TOKEN)
     response = sc.api_call("chat.postMessage", channel=slackchannel, blocks=blockmessage)
    
     if not 'ok' in response or not response['ok']:
       print("Error posting message to Slack channel")
       print(blockmessage)
       print(response)
     else:
       print("Ok posting message to Slack channel")
      
   return HttpResponse("Thanks, Sensei/Kanji/SlackWebHook", status=200)   

#  09-17-2019 
#  Acknowledge Events
#   
def slack(request):
   #process POST requests from Slack when a user selects a button
   log.error("INFO view/slack has been called!")
   payload = request.body.decode("utf-8")
   payload = urllib.parse.parse_qs(payload)
   payload = json.loads(payload['payload'][0])
   #log.error(payload)
   #log.error("payload {0}".format(payload["actions"][0]))
   action = payload["actions"][0]
   #log.error(action)
   log.error(payload["user"])
   slackuserid = payload["user"]['id']
   log.error("Event acked by {}".format(slackuserid))
   
   actionname = action["value"]
   actiontarget = action["action_id"]
   
   #we lookup the event of the action target and set the act fields'   
   event = EventLog.objects.get(pk=int(actiontarget))
   user = User.objects.filter(slackuserid=slackuserid)[0]
   
   if event:
     now = datetime.now()
     timestamp = now.strftime("%I:%M %p %A, %B %e, %Y")
     _SLACK_TOKEN = event.node.location.customer.slacktoken
     slackchannel = event.node.location.slackchannel
     log.error("slackChannel={0} slackToken={1}".format(slackchannel,_SLACK_TOKEN))
   
     config = configparser.ConfigParser()
     config.read('secrets.conf')
        
     #log.error("Calling {0} on coreid={1}".format(actionname,device.coreid))
   
     #_PARTICLE_TOKEN = config['DEFAULT']['_PARTICLE_TOKEN']
     #log.error("secrets _PARTICLE_TOKEN {0}".format(_PARTICLE_TOKEN))
   
     #actionurl = "https://api.particle.io/v1/devices/{0}/{1}".format(device.coreid,actionname)
     #log.error(actionurl)
     #data = {'access_token' : _PARTICLE_TOKEN, 'arg' : ""}
     #resp = requests.post(actionurl, data = data, timeout=(15, 30))
     #response = resp.json()
     #log.error("response={0}".format(response))
   
     #log.error("secrets _SLACK_TOKEN {0}".format(_SLACK_TOKEN)) 

     # set the event acktimestamp
     event.acktimestamp = now
     event.ackuser = user
     event.save()
   
     messagestring = "[\
       {\"type\": \"section\", \
		 \"text\": { \
			\"type\": \"mrkdwn\", \
			\"text\": \"*<fakeLink.toUserProfiles.com|Iris / Zelda 1-1>*\\nTuesday, January 21 4:00-4:30pm\\nBuilding 2 - Havarti Cheese (3)\\n2 guests\" \
		 }, \
		 \"accessory\": { \
			\"type\": \"image\", \
			\"image_url\": \"https://api.slack.com/img/blocks/bkb_template_images/notifications.png\", \
			\"alt_text\": \"calendar thumbnail\" \
		 } \
     }]"
    
     blockmessage = json.loads(messagestring)
   
     blockmessage[0]["accessory"]["image_url"] = "https://www.dropbox.com/s/2vvxy36e3jblulb/check.png?raw=1"
     blockmessage[0]["accessory"]["alt_text"] = "Ok thumbnail"
     blockmessage[0]["text"]["text"] = "at *{}* {} {} acknowledged *{}* event #{}".format(timestamp, user.firstname, user.lastname, event.node.location.description, event.ideventlog)
        
     sc = SlackClient(_SLACK_TOKEN)
     response = sc.api_call("chat.postMessage", channel=slackchannel, blocks=blockmessage)
    
     if not 'ok' in response or not response['ok']:
       print("Error posting message to Slack channel")
       print(blockmessage)
       print(response)
     else:
       print("Ok posting message to Slack channel")
      
   return HttpResponse("Thanks, Sensei/Kanji/SlackWebHook", status=200)   
   
def webhook(request):
   #
   # /kanji/webhooks will bring you here
   # this is for posting event data only from the Particle Cloud
   log.debug("DEBUG view/webhook has been called!") 
 
   str_content = request.body.decode("utf-8")
   print(str_content)
   json_data = json.loads(str_content.replace("'",'"'))
   
   event = json_data['event']
   data = json_data['data']
   coreid = json_data['coreid']
   published_at = json_data['published_at']
   timestamp = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%S.%fZ')
    
   dataParts = data.split("/")  
   
   doc = dataParts[0]   
   acktime = dataParts[1]   
   
   pins = json.loads(doc)   
   for pin in pins:
      log.debug("DEBUG view/webhook pin={0}".format(pin))
   
   sensorid = pin["t"]   

   eventlog = EventLog()
   eventlog.timestamp = timestamp
   eventlog.node = Node.objects.all().filter(coreid=coreid).first()
   eventlog.sensortype = SensorType.objects.get(pk=sensorid)
   eventlog.eventdata = doc
   eventlog.meshacktimemillis = int(acktime)
   
   #  09-17-2019  Urgency & Impact
   #  Event impact & urgency are set by the EventScanner script
   #   
   
   eventlog.save()
   
   log.debug("DEBUG view/webhook data={0}".format(data))
   log.debug("DEBUG view/webhook ackTime={0}".format(acktime))
   log.debug("DEBUG view/webhook core={0}".format(eventlog.node.name))
   log.debug("DEBUG view/webhook iddevice={0}".format(coreid))
   log.debug("DEBUG view/webhook sensorid={0}".format(sensorid))
   log.debug("DEBUG view/webhook doc={0}".format(doc))
   
   log.error("view/webhook called by core {0}".format(coreid))
   
   return HttpResponse("Thanks, Sensei/Kanji")