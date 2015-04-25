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
    url(r'^viewReport/(?P<number>.*)$', views.viewReport, name='viewReport'),
    url(r'^giveAdminAccess/$', views.giveAdminAccess, name = 'giveAdminAccess'),
    url(r'^makeGroup/$', views.makeGroup, name='makeGroup'),
   	url(r'^addUserToGroup/$', views.addUserToGroup, name = 'addUserToGroup'),
    url(r'^addToGroupUser/$', views.addToGroupUser, name = 'addToGroupUser'),
    url(r'^changeUserSuspensionStatus/$', views.changeUserSuspensionStatus, name = 'changeUserSuspensionStatus'),
    url(r'^deleteReport/(?P<desc>.*)', views.deleteReport, name = 'deleteReport'),
    url(r'^login_decrypt/$', views.login_decrypt, name = 'login_decrpyt'),
    url(r'^viewFiles_decrypt/$', views.viewFiles_decrypt, name = 'viewFiles_decrpyt'),
    url(r'^viewReports_decrypt/$', views.viewReports_decrypt, name = 'viewReports_decrpyt'),
    url(r'^uploaded_key/$', views.uploaded_key, name = 'uploaded_key'),
    url(r'^viewAvailableReports/$', views.viewAvailableReports, name = 'viewAvailableReports'),
    url(r'^logout/$', views.logout_view, name='logout'),
)