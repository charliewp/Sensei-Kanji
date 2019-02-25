from django.db import models

# SensorDB Models

from datetime import datetime
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.core.validators import RegexValidator
from django.contrib.contenttypes.models import ContentType

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class EventType(models.Model):
    ideventtype  = models.BigAutoField(primary_key=True)
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
    def __str__(self):
        return self.name
    
class Location(models.Model):
    idlocation  = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=24)
    customer = models.ForeignKey(Customer,on_delete=models.PROTECT, default=10000) 
    def __str__(self):
        return self.description

class Node(models.Model):
    idnode  = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=24)
    coreid = models.CharField(max_length=24)
    coretype = models.ForeignKey(CoreType,on_delete=models.PROTECT,  null=True)
    deploystate = models.ForeignKey(DeployState,on_delete=models.PROTECT,  null=True)
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
    
class EventLog(models.Model):
    ideventlog = models.BigAutoField(primary_key=True)
    timestamp = models.DateTimeField(("DateTime"),auto_now_add=True)
    node = models.ForeignKey(Node,on_delete=models.PROTECT, default=1)
    eventtype = models.ForeignKey(EventType,on_delete=models.PROTECT, default=1)
    sensortype = models.ForeignKey(SensorType,on_delete=models.PROTECT, default=1)
    eventdata = models.CharField(max_length=24)
    meshacktimemillis = models.IntegerField(default=0)    

class PingLog(models.Model):
    idpinglog = models.BigAutoField(primary_key=True)
    timestamp = models.DateTimeField(("DateTime"),auto_now_add=True)
    node = models.ForeignKey(Node,on_delete=models.PROTECT, default=1)
    pingstate = models.ForeignKey(OnlineState,on_delete=models.PROTECT, null=True)