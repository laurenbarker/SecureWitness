from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from SecureWitness.models import report,user
from django.db.models import Q
from django.contrib.admin import widgets
from SecureWitness.forms import GiveAdminAccessForm
import os

#put forms in forms.py later
from django import forms
class loginForm(forms.Form):
    username =  forms.CharField(max_length=50)
    password =  forms.CharField(max_length=50)
    Register = forms.BooleanField(required=False)

class NameForm(forms.Form):
    desc = forms.CharField(label='Description Search Criteria', max_length=100, required=False)
    loc_and = forms.BooleanField(required=False, label="AND")
    loc_or = forms.BooleanField(required=False, label = "OR")
    loc = forms.CharField(label="Location Search", max_length=50,required=False)
    key_and = forms.BooleanField(required=False, label="AND")
    key_or = forms.BooleanField(required=False, label = "OR")
    key = forms.CharField(label="Keyword Search", max_length=50,required=False)
    inc_and = forms.BooleanField(required=False, label="AND")
    inc_or = forms.BooleanField(required=False, label = "OR")
    inc_start = forms.DateField(label="Incident Start Date", widget=widgets.AdminDateWidget(),required=False)
    inc_end = forms.DateField(label="Incident End Date", widget=widgets.AdminDateWidget(),required=False)


class UploadFileForm(forms.Form):
    shortdesc = forms.CharField(max_length=50)
    longdesc = forms.CharField(max_length=300)
    location = forms.CharField(max_length=50, required=False)
    incident_date = forms.DateField(required=False, widget=widgets.AdminDateWidget())
    keywords = forms.CharField(max_length=50, required=False)
    private = forms.BooleanField(required=False)
    file = forms.FileField(required=False)

def login(request):
        # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = loginForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # redirect to a new URL:
            u = request.POST.get('username')
            pw = form.cleaned_data['password']
            users = user.objects.filter(username=u).filter(password=pw)
            if(form.cleaned_data['Register']):
                if(len(user.objects.filter(username=u)) > 0):
                    return HttpResponse('username already taken')
                else:
                    newuser = user(username=u, password=pw)
                    newuser.save()
                    return HttpResponse("new user created successfully")
            elif(len(users) > 0):
                request.session['u'] = u
                if users[0].adminStatus == 1:
                    form = GiveAdminAccessForm()
                    return render(request, 'SecureWitness/adminPage.html', { 'form' : form })
                else:
                    return render(request, 'SecureWitness/userhome.html', {'u' : u})
            else:
                return HttpResponse("unsuccessful login")
    # if a GET (or any other method) we'll create a blank form
    else:
        form = loginForm()
    return render(request, 'SecureWitness/login.html', {'form': form})

def index(request):
    if 'u' in request.session:
        name = request.session['u']
        u = user.objects.filter(username=name)[0]
        report_list = report.objects.filter(author=u, folder = None)
        folder_list = report.objects.exclude(folder=None).filter(author=u)
        folders = {}
        for item in folder_list:
            if item.folder not in folders:
                folders[item.folder] = 1
            else:
                folders[item.folder] += 1
        template = loader.get_template('SecureWitness/index.html')
        context = RequestContext(request, {
            'report_list': report_list,
            'user' : request.session['u'],
            'folder_list' : folders
        })
        return render(request, 'SecureWitness/index.html', {
            'report_list': report_list,
            'user' : request.session['u'],
            'folder_list' : folders
        })
    else:
        return HttpResponse("You are not logged in")

#search
def search(request):
    #All search criteria is optional. If no search criteria is provided, it produces an empty list.
    #If no AND or OR option is selected, OR is used by default.
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            loclist = []
            keylist = []
            desclist = []
            inc_list = []
            keyword = request.POST.get('desc')
            if keyword is not None:
                keyword = keyword.split()
                for word in keyword:
                    qs =  report.objects.filter(Q(shortdesc__icontains=word) | Q(longdesc__icontains=word))
                    desclist.extend(qs)
            desclist = set(desclist)
            loc = request.POST.get('loc')
            if loc is not None:
                loc = loc.split()
                for word in loc:
                    qs = report.objects.filter(Q(location__icontains=word))
                    loclist.extend(qs)
            loclist = set(loclist)

            key = request.POST.get('key')
            if key is not None:
                key = key.split()
                for word in key:
                    qs = report.objects.filter(Q(keywords__icontains=word))
                    keylist.extend(qs)
                keylist = set(keylist)
            inc_start = request.POST.get('inc_start')
            inc_end = request.POST.get('inc_end')
            if inc_start and inc_end:
                inc_start = inc_start.split("/")
                inc_start = inc_start[2] + "-" + inc_start[0] + "-" + inc_start[1]
                inc_end = inc_end.split("/")
                inc_end = inc_end[2] + "-" + inc_end[0] + "-" + inc_end[1]
                inc_list = report.objects.filter(incident_date__range=(inc_start,inc_end))

            if(form.cleaned_data['loc_and']):
                desclist = list(set(desclist) & set(loclist))
            else:
                desclist = list(set(desclist) | set(loclist))
            if(form.cleaned_data['key_and']):
                desclist = list(set(desclist) & set(keylist))
            else:
                desclist = list(set(desclist) | set(keylist))
            if(form.cleaned_data['inc_and']):
                desclist = list(set(desclist) & set(inc_list))
            else:
                desclist = list(set(desclist) | set(inc_list))
            template = loader.get_template('SecureWitness/index.html')
            context = RequestContext(request, {
                  'report_list': desclist,
            })
            return HttpResponse(template.render(context))
    # if a GET (or any other method) we'll create a blank form
    elif 'u' in request.session:
        form = NameForm()
        return render(request, 'SecureWitness/search.html', {'form': form})
    else:
        return HttpResponse('You are not logged in')
#upload reports
def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            short = form.cleaned_data['shortdesc']
            long = form.cleaned_data['longdesc']
            loc = request.POST.get('location')
            if form.cleaned_data['incident_date'] is None:
                date = None
            else:
                #convert date format to YYYY-MM-DD from MM/DD/YYYY
                inc = request.POST.get('incident_date')
                date = inc.split("/")
                date = date[2] + "-" + date[0] + "-" + date[1]
            key = request.POST.get('keywords')
            priv = request.POST.get('private')
            if priv is None:
                priv = False
            f = request.FILES.get('file')
            #Once login is finished, get current logged i   n user
            name = request.session['u']
            u = user.objects.filter(username=name)[0]
            rep = report(author = u, shortdesc = short, longdesc = long, location = loc, incident_date = date, keywords = key, private = priv, file = f, folder = None)
            rep.save()
            return HttpResponse("added successfully")
        else:
            return HttpResponse("form was not filled out correctly")
    elif 'u' in request.session:
        form = UploadFileForm()
        return render(request,'SecureWitness/upload.html', {'form': form})
    else:
        return HttpResponse('You are not logged in')

def adminPage(request):
    if request.method == 'POST':
        form = GiveAdminAccessForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['username']
            try: 
                users = user.objects.get(username=name)
                users.adminStatus = 1
                users.save()
                return HttpResponse("User was given admin access")
            except:
                return HttpResponse("User does not exist")
    else:
        form = GiveAdminAccessForm()
        return render(request, 'SecureWitness/adminPage.html', { 'form' : form })

def homepage(request):
        return render(request, 'SecureWitness/homepage.html')

def viewFolder(request, folder=""):
    name = request.session['u']
    u = user.objects.filter(username=name)[0]
    report_list = report.objects.filter(folder = folder).filter(author=u)
    template = loader.get_template('SecureWitness/viewFolder.html')
    context = RequestContext(request, {
            'report_list': report_list,
            'user' : request.session['u'],
            'folder_name' : folder
    })
    return HttpResponse(template.render(context))

def deleteFolder(request, folder=""):
    report_list = report.objects.filter(folder = folder).delete()
    if 'u' in request.session:
        name = request.session['u']
        u = user.objects.filter(username=name)[0]
        report_list = report.objects.filter(author=u, folder = None)
        folder_list = report.objects.exclude(folder=None).filter(author=u)
        folders = {}
        for item in folder_list:
            if item.folder not in folders:
                folders[item.folder] = 1
            else:
                folders[item.folder] += 1
        template = loader.get_template('SecureWitness/index.html')
        context = RequestContext(request, {
            'report_list': report_list,
            'user' : request.session['u'],
            'folder_list' : folders
        })
        return HttpResponse(template.render(context))
    else:
        return HttpResponse("You are not logged in")

def renameFolder(request, folder=""):
    if 'u' in request.session:
        new = request.POST['new']
        report_list = report.objects.filter(folder=folder)
        for x in report_list:
            x.folder = new
            x.save()
        name = request.session['u']
        template = loader.get_template('SecureWitness/viewFolder.html')
        context = RequestContext(request, {
                'report_list': report_list,
                'user' : request.session['u'],
                'folder_name' : new
        })
        return HttpResponse(template.render(context))
    else:
        return HttpResponse("You are not logged in")