from datetime import datetime
from django.utils import timezone
from datetime import timedelta
import operator
import json
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
from .models import Node
from .models import EventType
from .models import SensorType

from django.views.decorators.csrf import ensure_csrf_cookie
@ensure_csrf_cookie



# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the Sensei-Kanji index page.")
    
def chart(request):
    if request.method == 'GET':
        coreid = request.GET.get('coreid')
        #data  and array of arrays
        #[
        #    ['1986', 3.6, 2.3, 2.8, 11.5],
        #    ['1987', 7.1, 4.0, 4.1, 14.1],
        #    ['1988', 8.5, 6.2, 5.1, 17.5]
        #]
        series = []
        series.append(str("Temp"))
        #series.append("RPM")
        #series.append("Humidity")
        #series.append("Wind Speed")
        data = []
        #data.append( ["1986", 3.6, 2.3, 2.8, 11.5])
        #data.append( ["1987", 7.1, 4.0, 4.1, 14.1])
        #data.append( ["1988", 8.5, 6.2, 5.1, 17.5])
        #data.append( ["1989", 9.2, 11.8, 6.5, 18.9])
        #data.append( ["1990", 10.1, 13.0, 12.5, 20.8])
        #data.append( ["1991", 11.6, 13.9, 18.0, 22.9])
        #data.append( ["1992", 16.4, 18.0, 21.0, 25.2])
        #data.append( ["1993", 18.0, 23.3, 20.3, 27.0])
        #data.append( ["1994", 13.2, 24.7, 19.2, 26.5])
        #data.append( ["1995", 12.0, 18.0, 14.4, 25.3])
        #data.append( ["1996", 3.2, 15.1, 9.2, 23.4])
        #data.append( ["1997", 4.1, 11.3, 5.9, 19.5])
        #data.append( ["1998", 6.3, 14.2, 5.2, 17.8])
        #data.append( ["1999", 9.4, 13.7, 4.7, 16.2])
        #data.append( ["2000", 11.5, 9.9, 4.2, 15.4])
        #data.append( ["2001", 13.5, 12.1, 1.2, 14.0])
        #data.append( ["2002", 14.8, 13.5, 5.4, 12.5])
        #data.append( ["2003", 16.6, 15.1, 6.3, 10.8])
        #data.append( ["2004", 18.1, 17.9, 8.9, 8.9])
        #data.append( ["2005", 17.0, 18.9, 10.1, 8.0])
        #data.append( ["2006", 16.6, 20.3, 11.5, 6.2])
        #data.append( ["2007", 14.1, 20.7, 12.2, 5.1])
        #data.append( ["2008", 15.7, 21.6, 10, 3.7])
        #data.append( ["2009", 12.0, 22.5, 8.9, 1.5])
        
        node = Node.objects.all().filter(coreid=coreid).first()
        
        eventLogs = EventLog.objects.all().filter(node=node).filter(sensortype_id=7)
        
        for eventLog in eventLogs:
            date_time = eventLog.timestamp.strftime("%m/%d/%Y, %H:%M:%S")
            data.append([date_time, float(eventLog.eventdata)])
        
        print(data)
        
        return render(request, 'chart.html',  {'data': data, 'series': series})
          
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