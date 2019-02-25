from django.contrib import admin

# Register your models here.
from .models import EventType    
from .models import SensorType
from .models import CoreType
from .models import OnlineState
from .models import DeployState
from .models import Firmware
from .models import Application
from .models import Customer
from .models import Location
from .models import Node
from .models import EventLog
from .models import PingLog

admin.site.register(EventType)
admin.site.register(SensorType)
admin.site.register(CoreType)
admin.site.register(OnlineState)
admin.site.register(DeployState)
admin.site.register(Firmware)
admin.site.register(Application)
admin.site.register(Customer)
admin.site.register(Location)
admin.site.register(Node)
admin.site.register(EventLog)
admin.site.register(PingLog)

