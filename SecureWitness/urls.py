from django.conf.urls import patterns, url
from django.conf import settings

from SecureWitness import views

urlpatterns = patterns('',
    url(r'^index$', views.index, name='index'),
    url(r'^search/$', views.search, name='search'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^login/$', views.login, name='login'),
    url(r'^adminPage/$', views.adminPage, name='adminPage'),
    url(r'^homepage/$', views.homepage, name='homepage'),
    url(r'^uploaded_files/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT + "/uploaded_files"}),
    url(r'^viewFolder/(?P<folder>.*)$', views.viewFolder, name='viewFolder'),
    url(r'^deleteFolder/(?P<folder>.*)$', views.deleteFolder, name='deleteFolder'),
    url(r'^renameFolder/(?P<folder>.*)$', views.renameFolder, name='renameFolder'),
)