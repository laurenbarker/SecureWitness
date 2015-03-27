from django.conf.urls import patterns, url

from SecureWitness import views

urlpatterns = patterns('',
    url(r'^index$', views.index, name='index'),
    url(r'^search/$', views.search, name='search'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^adminPage/$', views.adminPage, name='adminPage'),
)