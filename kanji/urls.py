from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url

from . import views

urlpatterns = [ 
	url(r'customer/*', views.index, name='index'),
    url(r'node/*', views.node, name='node'),
    url(r'channel/*', views.channel, name='channel'),
    url(r'dashboard/*', views.dashboard, name='dashboard'),
    url(r'webhook', views.webhook, name='webhook'),
    url(r'slack', views.slack, name='slack'), 
    url(r'squealer', views.squealer, name='squealer'),    
]