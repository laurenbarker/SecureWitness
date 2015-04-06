from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from SecureWitness.models import report,user, group
from django.db.models import Q
from django.contrib.admin import widgets
import os
from SecureWitness.forms import GiveAdminAccessForm, CreateGroupForm, addUserForm, suspendUserForm
import json
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random
from django.conf import settings

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
                elif users[0].suspensionStatus == 1:
                    return HttpResponse('Your account has been suspended by an administrator')
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

            # public/private key pair
            random_generator = Random.new().read
            key = RSA.generate(1024, random_generator)

            # encrypt
            public_key = key.publickey()
            # change

            newName = f.name + "_enc"

            path2 = os.path.join(settings.MEDIA_ROOT, 'uploaded_files', newName)
            myf = open(path2, "w+b")

            #wipe the existing content
            #f.truncate()

            for chunk in f.chunks():
                enc_data = public_key.encrypt(chunk, 32)
                myf.write(str(enc_data))

            f.name = path2

            name = request.session['u']
            u = user.objects.filter(username=name)[0]
            rep = report(author = u, shortdesc = short, longdesc = long, location = loc, incident_date = date, keywords = key, private = priv, file = f, folder = None)
            rep.f = myf
            rep.save()
            return HttpResponse("added successfully")
        else:
            return render(request,'SecureWitness/upload.html', {'form': form})
    elif 'u' in request.session:
        form = UploadFileForm()
        return render(request,'SecureWitness/upload.html', {'form': form})
    else:
        return HttpResponse('You are not logged in')

def homepage(request):
    if 'u' in request.session:
        u = request.user.username
        return render(request, 'SecureWitness/userhome.html', {'u' : u})
    else:
        return render(request, 'SecureWitness/homepage.html')

def adminPage(request):
    return render(request, 'SecureWitness/adminPage.html')

def giveUserAccess(request):
    if request.method == 'POST':
        form = GiveAdminAccessForm()
        return render(request, 'SecureWitness/giveAdminAccess.html', { 'form' : form })

def giveAdminAccess(request):
    if request.method == 'POST':
        form = GiveAdminAccessForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['username'].strip()

            try: 
                users = user.objects.get(username=name)
                users.adminStatus = 1
                users.save()
                return HttpResponse("User was given admin access")
            except:
                return HttpResponse("User does not exist")

        else:
            return HttpResponse("Please enter a user")
    else:
        form = GiveAdminAccessForm()
        return render(request, 'SecureWitness/adminPage.html', { 'form' : form })

def createGroup(request):
    if request.method == 'POST':
        form = CreateGroupForm()
        return render(request, 'SecureWitness/createGroup.html', { 'form' : form } )

def viewFolder(request, folder=""):
    if 'u' in request.session:
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
    else:
         return HttpResponse("You are not logged in")

def viewReport(request, desc=""):
    if 'u' in request.session:
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            short = request.POST.get('shortdesc')
            long = request.POST.get('longdesc')
            loc = request.POST.get('location')
            inc = request.POST.get('incident_date')
            if inc is None or inc == "":
                date = None
            else:
                #convert date format to YYYY-MM-DD from MM/DD/YYYY
                date = inc.split("/")
                date = date[2] + "-" + date[0] + "-" + date[1]
            key = request.POST.get('keywords')
            priv = request.POST.get('private')
            if priv is None:
                priv = False
            f = request.FILES.get('file')
            name = request.session['u']
            u = user.objects.filter(username=name)[0]
            report_list = report.objects.filter(shortdesc=desc).filter(author=u)[0]
            if short:
                report_list.shortdesc = short
            if long:
                report_list.longdesc = long
            if loc:
                report_list.location = loc
            report_list.incident_date = date
            if key:
                report_list.keywords = key
            report_list.private = priv
            if f:
                report_list.file = f
            report_list.save()
            form = UploadFileForm()
            #return HttpResponse(template.render(context))
            if short:
                return HttpResponseRedirect( short)
            else:
                return HttpResponseRedirect( report_list.shortdesc)
        else:
            name = request.session['u']
            u = user.objects.filter(username=name)[0]
            report_list = report.objects.filter(shortdesc=desc).filter(author=u)[0]
            template = loader.get_template('SecureWitness/viewReport.html')
            form = UploadFileForm()
            context = RequestContext(request, {
                    'report': report_list,
                    'user' : request.session['u'],
                    'form' : form,
            })
            return HttpResponse(template.render(context))
    else:
         return HttpResponse("You are not logged in")

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

def makeGroup(request):
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['groupName']
            if group.objects.filter(groupName = name).exists():
                return HttpResponse("Group already exists")
            else:
                users = {}
                users[name] = []
                myGroup = group(groupName = name, users = json.dumps(users))
                myGroup.save()
                return HttpResponse("Group was successfully created!")

def addUser(request):
    if request.method == 'POST':
        form = addUserForm()
        return render(request, 'SecureWitness/addUser.html', { 'form' : form })

def addUserToGroup(request):
    if request.method == 'POST':
        form = addUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'].strip()
            groupname = form.cleaned_data['toGroup'].strip()
            if group.objects.filter(groupName = groupname).exists() and user.objects.filter(username = username).exists():
                theGroup = group.objects.get(groupName=groupname)
                users = json.loads(theGroup.users)
                if username not in users[groupname]:
                    users[groupname].append(username)
                    theGroup.users = json.dumps(users)
                    theGroup.save()
                    return HttpResponse("User was successfully added")
                else:
                    return HttpResponse("User is already in this group")
            else:
                return HttpResponse("Please enter a valid username AND a valid group name")
        else:
            return HttpResponse("Please enter a username and a group name.")
    else:
        form = addUserForm()
        return render(request, 'SecureWitness/addUser.html', {'form' : form })

def suspendUser(request):
    if request.method == 'POST':
        form = suspendUserForm()
        return render(request, 'SecureWitness/changeUserSuspensionStatus.html', { 'form' : form })

def changeUserSuspensionStatus(request):
    if request.method == 'POST':
        form = suspendUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'].strip()
            try: 
                users = user.objects.get(username=username)
                if 'suspend' in request.POST:
                    users.suspensionStatus = 1
                    users.save()
                    return HttpResponse("User was suspended")
                else:
                    users.suspensionStatus = 0
                    users.save()
                    return HttpResponse("User was unsuspended")
            except:
                return HttpResponse("User does not exist")
        else:
            return HttpResponse("Please enter a username")
    else:
        form = suspendUserForm()
        return render(request, 'SecureWitness/suspendUser.html', { 'form' : form })
