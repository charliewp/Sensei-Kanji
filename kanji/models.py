from django.db import models

# SensorDB Models

from datetime import datetime
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.core.validators import RegexValidator
from django.contrib.contenttypes.models import ContentType

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Impact(models.Model):
    idimpact  = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=24)
    def __str__(self):
        return self.description 
        
class Urgency(models.Model):
    idurgency = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=24)
    def __str__(self):
        return self.description

class TicketStatus(models.Model):
    idticketstatus = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=24)
    def __str__(self):
        return self.description               
    
class SensorType(models.Model):
    idsensortype  = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=32)
    shorttag = models.CharField(max_length=32, default='none')
    units = models.CharField(max_length=32, default='none')
    def __str__(self):
        return self.description
        
class NodeType(models.Model):
    idnodetype  = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=32)
    shorttag = models.CharField(max_length=32, default='none')
    def __str__(self):
        return self.description
    
class CoreType(models.Model):
    idcoretype  = models.BigAutoField(primary_key=True)
    manufacturer = models.CharField(max_length=24, default='none')
    model = models.CharField(max_length=24, default='none')
    def __str__(self):
        return self.manufacturer + " " + self.model
    
class OnlineState(models.Model):
    idonlinestate  = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=24)
    def __str__(self):
        return self.description
    
class DeployState(models.Model):
    iddeploystate  = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=24)
    def __str__(self):
        return self.description    
    
class Firmware(models.Model):
    idfirmware  = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=24)
    def __str__(self):
        return self.description
    
class Application(models.Model):
    idapplication  = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=24)
    def __str__(self):
        return self.description
    
class Customer(models.Model):
    idcustomer  = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=24)
    slacktoken = models.CharField(max_length=128, null=True)
    slackworkspace = models.CharField(max_length=128, null=True)
    slackadminuser = models.CharField(max_length=64, null=True)
    slackadminpass = models.CharField(max_length=64, null=True)
    def __str__(self):
        return self.name
    
class Location(models.Model):
    idlocation  = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=64)
    zipcode = models.CharField(max_length=10, null=True)
    imageurl = models.CharField(max_length=128, null=True)
    customer = models.ForeignKey(Customer,on_delete=models.PROTECT, default=10000) 
    slackchannel = models.CharField(max_length=32, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    #some fields to impose range limits on sensors
    maxtempf = models.IntegerField(null=False, default=95) 
    mintempf  = models.IntegerField(null=False, default=32) 
    maxpsi = models.IntegerField(null=False, default=100) 
    minpsi = models.IntegerField(null=False, default=30) 
    maxrssidb = models.IntegerField(null=False, default=0) 
    minrssidb = models.IntegerField(null=False, default=-78) 
    maxvolts = models.IntegerField(null=False, default=140) 
    minvolts = models.IntegerField(null=False, default=100) 
    maxo2pct = models.IntegerField(null=False, default=100) 
    mino2pct = models.IntegerField(null=False, default=20) 
    
    def __str__(self):
        return self.description

class Channel(models.Model):
    idchannel = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=24, null=True)
    uplink = models.IntegerField(null=False)
    dnlink = models.IntegerField(null=False)
    
class MeshNetwork(models.Model):
    idmeshnetwork = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=24)
    password = models.CharField(max_length=24)
    
class User(models.Model):
    iduser = models.BigAutoField(primary_key=True)
    firstname = models.CharField(max_length=24)
    lastname = models.CharField(max_length=24)
    slackuserid = models.CharField(max_length=24)
    password = models.CharField(max_length=24)
    
class TicketType(models.Model):
    idtickettype = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=64, null=True)
    
class Node(models.Model):
    idnode  = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=24)
    friendlyname = models.CharField(max_length=32, null=True)
    coreid = models.CharField(max_length=24)
    coretype = models.ForeignKey(CoreType,on_delete=models.PROTECT,  null=True)
    nodetype = models.ForeignKey(NodeType,on_delete=models.PROTECT,  null=True, default=10000)
    deploystate = models.ForeignKey(DeployState,on_delete=models.PROTECT,  null=True)
    channel = models.ForeignKey(Channel,on_delete=models.PROTECT,  null=True)
    meshnetwork = models.ForeignKey(MeshNetwork,on_delete=models.PROTECT,  null=True)
    setupstring = models.CharField(max_length=64, null=True)
    gridlocator = models.CharField(max_length=8, null=True)
    startofservicedate = models.DateField(null=True, blank=True)
    endofservicedate = models.DateField(null=True, blank=True)
    firmware =  models.ForeignKey(Firmware,on_delete=models.PROTECT, null=True)
    application = models.ForeignKey(Application,on_delete=models.PROTECT, null=True)
    location = models.ForeignKey(Location,on_delete=models.PROTECT, null=True)
    customer = models.ForeignKey(Customer,on_delete=models.PROTECT, null=True)
    lastpingtimestamp = models.DateTimeField(("Last Ping Time"), null=True)
    lastpingstate = models.ForeignKey(OnlineState,on_delete=models.PROTECT, null=True)
    pingintervalmillis = models.IntegerField(null=False)
    def __str__(self):
        return self.name 
        
class Ticket(models.Model):
    idticket = models.BigAutoField(primary_key=True)
    node = models.ForeignKey(Node,on_delete=models.PROTECT, null=True)
    description = models.CharField(max_length=128, null=True)
    type = models.ForeignKey(TicketType,on_delete=models.PROTECT, null=True)
    location = models.ForeignKey(Location,on_delete=models.PROTECT, null=True)
    opentimestamp = models.DateTimeField(("DateTime"),auto_now_add=True)
    status = models.ForeignKey(TicketStatus, on_delete=models.PROTECT, null=True)
    impact = models.ForeignKey(Impact, on_delete=models.PROTECT, null=True)
    urgency = models.ForeignKey(Urgency, on_delete=models.PROTECT, null=True)
    acktimestamp = models.DateTimeField(("DateTime"), null=True)
    ackuser = models.ForeignKey(User, on_delete=models.PROTECT, null=True)    
    closetimestamp = models.DateTimeField(("DateTime"), null=True)
    
class EventLog(models.Model):
    ideventlog = models.BigAutoField(primary_key=True)
    timestamp = models.DateTimeField(("DateTime"),auto_now_add=True)
    node = models.ForeignKey(Node,on_delete=models.PROTECT, default=1)
    #impact = models.ForeignKey(Impact, on_delete=models.PROTECT, null=True)
    #urgency = models.ForeignKey(Urgency, on_delete=models.PROTECT, null=True)
    #acktimestamp = models.DateTimeField(("DateTime"), null=True)
    #ackuser = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    sensortype = models.ForeignKey(SensorType,on_delete=models.PROTECT, default=1)
    eventdata = models.CharField(max_length=622)
    meshacktimemillis = models.IntegerField(default=0)    

class PingLog(models.Model):
    idpinglog = models.BigAutoField(primary_key=True)
    timestamp = models.DateTimeField(("DateTime"),auto_now_add=True)
    node = models.ForeignKey(Node,on_delete=models.PROTECT, default=1)
    pingstate = models.ForeignKey(OnlineState,on_delete=models.PROTECT, null=True)
      
class Sensor(models.Model):
    idsensor = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=24)
    node = models.ForeignKey(Node,on_delete=models.PROTECT, default=1)
    sensortype = models.ForeignKey(SensorType,on_delete=models.PROTECT, default=1)