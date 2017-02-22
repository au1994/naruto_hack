from django.conf.urls import url
from views import *
from . import views
from django.conf.urls import patterns, include, url

urlpatterns = patterns('naruto_app.views',
    url(r'^$', csrf_exempt(OrderList.as_view())),
)