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

from django.template import RequestContext, Template, Context

from slackclient import SlackClient
import urllib
from urllib.parse import urlparse
import requests

import logging
log = logging.getLogger('KANJI-LOGGER')

from django.views.decorators.csrf import ensure_csrf_cookie
@ensure_csrf_cookie

# Create your views here.
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
      
def slack(request):
   #POST from Slack when a user selects a button
   log.error("INFO view/slackwebhook has been called!")
   payload = request.body.decode("utf-8")
   payload = urllib.parse.parse_qs(payload)
   payload = json.loads(payload['payload'][0])
   
   log.error("payload {0}".format(payload["actions"][0]))
   action = payload["actions"][0]
   log.error(action)
   
   actionname = action["value"]
   actiontarget = action["action_id"]
   
   #we lookup the coreid of the action target and call the function named in 'actionname'
   
   device = Node.objects.get(pk=int(actiontarget))
   
   log.error("Calling {0} on coreid={1}".format(actionname,device.coreid))
   _PARTICLE_TOKEN = '790261410d6873b994fb6041553b5a99a7f7ed0e'
   actionurl = "https://api.particle.io/v1/devices/{0}/{1}".format(device.coreid,actionname)
   log.error(actionurl)
   data = {'access_token' : _PARTICLE_TOKEN, 'arg' : ""}
   resp = requests.post(actionurl, data = data, timeout=(15, 30))
   response = resp.json()
   log.error("response={0}".format(response))
   
   _SLACK_TOKEN = "xoxp-565796905971-565875952996-565171872688-7c596833100ecbfd4841a3f666c15be6"
   
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
	}, \
	{\"type\": \"context\", \
		\"elements\": [ \
			{ \
				\"type\": \"image\", \
				\"image_url\": \"https://www.dropbox.com/s/o2gjgfsph2cxgds/thermometer.jpg?raw=1\", \
				\"alt_text\": \"notifications warning icon\" \
			}, \
			{ \
				\"type\": \"mrkdwn\", \
				\"text\": \"*Conflicts with Team Huddle: 4:15-4:30pm*\" \
			} \
		] \
	}, \
    {\"type\": \"context\", \
		\"elements\": [ \
			{ \
				\"type\": \"image\", \
				\"image_url\": \"https://www.dropbox.com/s/pw6329yc2ge05cr/gear.png?raw=1\", \
				\"alt_text\": \"notifications warning icon\" \
			}, \
			{ \
				\"type\": \"mrkdwn\", \
				\"text\": \"*Conflicts with Team Huddle: 4:15-4:30pm*\" \
			} \
		] \
	}, \
    {\"type\": \"context\", \
		\"elements\": [ \
			{ \
				\"type\": \"image\", \
				\"image_url\": \"https://api.slack.com/img/blocks/bkb_template_images/notificationsWarningIcon.png\", \
				\"alt_text\": \"notifications warning icon\" \
			}, \
			{ \
				\"type\": \"mrkdwn\", \
				\"text\": \"*Controller is in SUPERVISORY MODE*\" \
			} \
		] \
	}, \
   	{ \
		\"type\": \"divider\" \
	}, \
    { \
		\"type\": \"section\", \
		\"text\": { \
			\"type\": \"mrkdwn\", \
			\"text\": \"*Accessory text.*\" \
		}, \
		\"accessory\": { \
			\"type\": \"button\", \
			\"text\": { \
				\"type\": \"plain_text\", \
				\"text\": \"BUTTON_TEXT\" \
			}, \
			\"value\": \"BUTTON_VALUE\", \
			\"action_id\": \"button\" \
		} \
	} \
]"

    
   blockmessage = json.loads(messagestring)
   blockmessage[0]["text"]["text"] = "*{0}*".format("The test was successful")

   
   sc = SlackClient(_SLACK_TOKEN)
   response = sc.api_call("chat.postMessage", channel="building-1", blocks=blockmessage)
    
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
   # this is for posting data only from the Particle Cloud
   log.debug("DEBUG view/webhook has been called!") 
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
   
   doc = dataParts[0]   
   acktime = dataParts[1]   
   
   pins = json.loads(doc)   
   for pin in pins:
      log.debug("DEBUG view/webhook pin={0}".format(pin))
   
   eventtype = 10000
   sensorid = pin["t"]   

   eventlog = EventLog()
   eventlog.timestamp = timestamp
   eventlog.node = Node.objects.all().filter(coreid=coreid).first()
   eventlog.eventtype = EventType.objects.get(pk=eventtype)
   eventlog.sensortype = SensorType.objects.get(pk=sensorid)
   eventlog.eventdata = doc
   eventlog.meshacktimemillis = int(acktime)  
   
   eventlog.save()
   
   log.debug("DEBUG view/webhook data={0}".format(data))
   log.debug("DEBUG view/webhook ackTime={0}".format(acktime))
   log.debug("DEBUG view/webhook core={0}".format(eventlog.node.name))
   log.debug("DEBUG view/webhook iddevice={0}".format(coreid))
   log.debug("DEBUG view/webhook publishtopic={0}".format(eventtype))
   log.debug("DEBUG view/webhook sensorid={0}".format(sensorid))
   log.debug("DEBUG view/webhook doc={0}".format(doc))
   
   log.error("view/webhook called by core {0}".format(coreid))
   
   return HttpResponse("Thanks, Sensei/Kanji")