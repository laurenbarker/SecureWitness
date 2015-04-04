from django.conf.urls import patterns, url

from SecureWitness import views

urlpatterns = patterns('',
    url(r'^index$', views.index, name='index'),
    url(r'^search/$', views.search, name='search'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^login/$', views.login, name='login'),
    url(r'^adminPage/$', views.adminPage, name='adminPage'),
    url(r'^giveUserAccess/$', views.giveUserAccess, name = 'giveUserAccess'),
    url(r'^giveAdminAccess/$', views.giveAdminAccess, name = 'giveAdminAccess'),
    url(r'^createGroup/$', views.createGroup, name='createGroup'),
    url(r'^makeGroup/$', views.makeGroup, name='makeGroup'),
    url(r'^addUser/$', views.addUser, name = 'addUser'),
   	url(r'^addUserToGroup/$', views.addUserToGroup, name = 'addUserToGroup'),
)