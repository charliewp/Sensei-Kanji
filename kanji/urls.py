from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url

from . import views

urlpatterns = [ 
	url(r'^$', views.index, name='index'),
    url(r'chart*', views.chart, name='chart'),
    url(r'webhook', views.webhook, name='webhook'),
    
]