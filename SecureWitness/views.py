from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from SecureWitness.models import report,user, group
from django.db.models import Q
from django.contrib.admin import widgets
import os
from SecureWitness.forms import GiveAdminAccessForm, CreateGroupForm, addUserForm, suspendUserForm, deleteReportForm
import json
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout

#put forms in forms.py later
from django import forms
from django.forms import PasswordInput

class loginForm(forms.Form):
    username =  forms.CharField(max_length=50)
    password =  forms.CharField(max_length=50, widget=PasswordInput)
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
    def __init__(self,group_list = [], Post = "", files=""):
        super(UploadFileForm, self).__init__()
        for group in group_list:
            self.fields["Give access to " + group] = forms.BooleanField(required=False)
    folder = forms.CharField(max_length=100, required=False)

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
                    return render(request, 'SecureWitness/login.html', {
                        'alreadytaken' : True,
                        'form' : loginForm(),
                    })
                else:
                    newuser = user(username=u, password=pw)
                    newuser.save()
                    return render(request, 'SecureWitness/login.html', {
                        'newuser' : True,
                        'form' : loginForm(),
                    })
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
                return render(request, 'SecureWitness/login.html', {
                    'nosuccess' : True,
                    'form' : loginForm(),
                })

    # if a GET (or any other method) we'll create a blank form
    else:
        form = loginForm()
    return render(request, 'SecureWitness/login.html', {'form': form})

def logout_view(request):
    logout(request)
    form = loginForm()
    return render(request, 'SecureWitness/homepage.html')

@csrf_exempt
def login_decrypt(request):
    # get username and password from app
    u = request.POST.get('username')
    pw = request.POST.get('password')
    # check and see if that user exists
    users = user.objects.filter(username=u).filter(password=pw)

    if(len(users) > 0):
        if users[0].adminStatus == 1:
            #form = GiveAdminAccessForm()
            return HttpResponse('You are an administrator')
        elif users[0].suspensionStatus == 1:
            return HttpResponse('Your account has been suspended by an administrator')
        else:
            return HttpResponse('Authentication succeeded.')
    else:
        return HttpResponse("unsuccessful authentication")

@csrf_exempt
def viewFiles_decrypt(request):
    # get reports for user
    name = request.POST.get('username')
    u = user.objects.filter(username=name)[0]
    report_list = report.objects.filter(Q(author=u) & (Q(folder = None) | Q(folder = "")))
    groups = group.objects.all()
    #create groups that have access to the report
    group_list = []
    for g in groups:
        users = json.loads(g.users)
        if u in users[g.groupName]:
            group_list.append(g.groupName)
    grp = ""
    for g in group_list:
        grp = grp + g

    #ob_list = report.objects.filter(reduce(lambda x, y: x | y, [Q(name__contains=word) for word in group_list]))
    return HttpResponse(str(report_list) + grp)
    #return HttpResponse(groups)

@csrf_exempt
def uploaded_key(request):
    # get reports for user
    name = request.POST.get('username')
    u = user.objects.filter(username=name)[0]
    report_list = report.objects.filter(Q(author=u) & (Q(folder = None) | Q(folder = "")))
    groups = group.objects.all()
    #create groups that have access to the report
    group_list = []
    for g in groups:
        users = json.loads(g.users)
        if u in users[g.groupName]:
            group_list.append(g.groupName)
    grp = ""
    for g in group_list:
        grp = grp + g

    #ob_list = report.objects.filter(reduce(lambda x, y: x | y, [Q(name__contains=word) for word in group_list]))
    #return HttpResponse(str(report_list) + grp)
    return HttpResponse("In progress...")

def index(request):
    if 'u' in request.session:
        name = request.session['u']
        u = user.objects.filter(username=name)[0]
        report_list = report.objects.filter(Q(author=u) & (Q(folder = None) | Q(folder = "")))
        folder_list = report.objects.exclude(folder=None).exclude(folder="").filter(author=u)
        folders = {}
        for item in folder_list:
            if item.folder not in folders:
                folders[item.folder] = 1
            else:
                folders[item.folder] += 1

        list = group.objects.all()
        group_list = []
        for g in list:
            if name in g.users:
                group_list.append(g.groupName)

        template = loader.get_template('SecureWitness/index.html')
        context = RequestContext(request, {
            'report_list': report_list,
            'user' : request.session['u'],
            'folder_list' : folders,
            'group_list' : group_list,
        })
        return render(request, 'SecureWitness/index.html', {
            'report_list': report_list,
            'user' : request.session['u'],
            'folder_list' : folders,
            'group_list' : group_list,
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

            #remove reports user is not authorized to see
            name = request.session['u']
            u = user.objects.filter(username=name)[0]
            if not u.adminStatus:
                groups = group.objects.all()
                #create groups user is in
                group_list = []
                for g in groups:
                    users = json.loads(g.users)
                    if request.session['u'] in users[g.groupName]:
                        group_list.append(g.groupName)
                for item in desclist:
                    if item.author != u and item.private:
                        authorization = False
                        for x in group_list:
                            if x in item.group:
                                authorization = True
                        if not authorization:
                            desclist.remove(item)

            template = loader.get_template('SecureWitness/index.html')
            context = RequestContext(request, {
                  'report_list': desclist,
                  'search' : 'yes',
                  'user' : request.session['u'],
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
        form = UploadFileForm([],request.POST, request.FILES)
        if request.POST.get('shortdesc') and request.POST.get('longdesc'):
            short = request.POST.get('shortdesc')
            long = request.POST.get('longdesc')
            loc = request.POST.get('location')
            if not request.POST.get('incident_date'):
                date = None
            else:
                #convert date format to YYYY-MM-DD from MM/DD/YYYY
                inc = request.POST.get('incident_date')
                date = inc.split("/")
                date = date[2] + "-" + date[0] + "-" + date[1]
            kwds = request.POST.get('keywords')
            priv = request.POST.get('private')
            group_access = {}
            if priv is None:
                priv = False
            else:
                 groups = group.objects.all()
                #create groups that have access to the report
                 group_list = []
                 for g in groups:
                    users = json.loads(g.users)
                    if request.session['u'] in users[g.groupName]:
                        group_list.append(g.groupName)
                    permission = request.POST.get("Give access to " + g.groupName)
                    if permission:
                        group_access[g.groupName] = True

            f = request.FILES.get('file')
            if f:
                # public/private key pair
                random_generator = Random.new().read
                key = RSA.generate(1024, random_generator)
                pkey = key.exportKey('PEM')

                # encrypt
                public_key = key.publickey()
                # change

                newName = f.name + "_enc"

                path2 = os.path.join(settings.MEDIA_ROOT, 'uploaded_files', newName)
                path = os.path.join('uploaded_files', newName)
                myf = open(path2, "w+b")

                for chunk in f.chunks():
                    enc_data = public_key.encrypt(chunk, 32)
                    myf.write(enc_data[0])


                f = path
            else:
                pkey = ""
            name = request.session['u']
            u = user.objects.filter(username=name)[0]
            fold = request.POST.get('folder')
            if not fold:
                fold = None
            rep = report(author = u, shortdesc = short, longdesc = long, location = loc, incident_date = date, keywords = kwds, private = priv, file = f, folder = fold, key = pkey)
            rep.group = json.dumps(group_access)
            if f:
                rep.f = myf
            rep.save()
            return HttpResponse("added successfully")
        else:
            return render(request,'SecureWitness/upload.html', {'form': form})
    elif 'u' in request.session:
        #get groups user is in
        group_list = []
        groups = group.objects.all()
        for g in groups:
            users = json.loads(g.users)
            if request.session['u'] in users[g.groupName]:
                group_list.append(g.groupName)
        form = UploadFileForm(group_list)
        return render(request,'SecureWitness/upload.html', {'form': form})
    else:
        return HttpResponse('You are not logged in')

def homepage(request):
    if 'u' in request.session:
        name = request.session['u']
        u = user.objects.filter(username=name)[0]

        return render(request, 'SecureWitness/userhome.html', {
            'user' : request.session['u'],
            'adminStat' : u.adminStatus,
        })
    else:
        return render(request, 'SecureWitness/homepage.html')

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
            if request.POST.get('del'):
                report_list = report.objects.filter(shortdesc=desc).delete()
                template = loader.get_template('SecureWitness/viewReport.html')
                context = RequestContext(request, {
                   'user' : request.session['u'],
                })
                return HttpResponse(template.render(context))
            else:
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
                fold = request.POST.get('folder')
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
                if fold:
                    report_list.folder = fold
                #get groups user is in
                group_list = []
                groups = group.objects.all()
                for g in groups:
                    users = json.loads(g.users)
                    if request.session['u'] in users[g.groupName]:
                        group_list.append(g.groupName)

                if priv:
                    report_groups = json.loads(report_list.group)
                    for g in group_list:
                        info = request.POST.get(g)
                        if info:
                            if g not in report_groups:
                                report_groups[g] = True
                        else:
                            if g in report_groups:
                                del report_groups[g]
                    report_list.group = json.dumps(report_groups)
                else:
                    report_list.group = json.dumps({})
                report_list.save()
                if short:
                    return HttpResponseRedirect( short)
                else:
                    return HttpResponseRedirect( report_list.shortdesc)
        else:
            name = request.session['u']
            u = user.objects.filter(username=name)[0]
            report_list = report.objects.filter(shortdesc=desc).filter(author=u)[0]
            template = loader.get_template('SecureWitness/viewReport.html')
            #get groups user is in
            group_list = []
            groups = group.objects.all()
            for g in groups:
                users = json.loads(g.users)
                if request.session['u'] in users[g.groupName]:
                    group_list.append(g.groupName)
            report_groups = report_list.group
            group_access = []
            form = UploadFileForm(group_list)
            group_dict = {}
            for g in group_list:
                if g in report_groups:
                    group_dict[g] = True
                else:
                    group_dict[g] = False
            context = RequestContext(request, {
                    'report': report_list,
                    'user' : request.session['u'],
                    'form' : form,
                    'groups' : group_dict
            })
            return HttpResponse(template.render(context))
    else:
         return HttpResponse("You are not logged in")

def viewAvailableReports(request):
    if 'u' in request.session:
        name = request.session['u']
        u = user.objects.filter(username=name)[0]
        report_list = report.objects.filter(Q(author=u) & (Q(folder = None) | Q(folder = "")) | Q(private=False))
        folder_list = report.objects.exclude(folder=None).exclude(folder="").filter(author=u)

        groups = group.objects.all()
        group_list = []
        for g in groups:
            users = json.loads(g.users)
            if request.session['u'] in users[g.groupName]:
                group_list.append(g.groupName)

        report_names = []

        for g in group_list:
            all_reports = report.objects.all()
            for a_report in all_reports:
                if g in a_report.group:
                    #GET REPORT BY UNIQUE IDENTIFIERS
                    report_names.append(a_report.shortdesc)

        group_report_list = report.objects.filter(shortdesc__in=report_names)

        report_list = report_list | group_report_list


        folders = {}
        for item in folder_list:
            if item.folder not in folders:
                folders[item.folder] = 1
            else:
                folders[item.folder] += 1

        list = group.objects.all()
        group_list = []
        for g in list:
            if name in g.users:
                group_list.append(g.groupName)

        template = loader.get_template('SecureWitness/availableReports.html')
        context = RequestContext(request, {
            'report_list': report_list,
            'user' : request.session['u'],
            'folder_list' : folders,
            'group_list' : group_list,
        })
        return render(request, 'SecureWitness/availableReports.html', {
            'report_list': report_list,
            'user' : request.session['u'],
            'folder_list' : folders,
            'group_list' : group_list,
        })
    else:
        return HttpResponse("You are not logged in")

def deleteFolder(request, folder=""):
    if 'u' in request.session:
        report_list = report.objects.filter(folder = folder).delete()
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

def addToGroupUser(request):
    if 'u' in request.session:
        groups = group.objects.all()
        group_list = []
        for g in groups:
            users = json.loads(g.users)
            if request.session['u'] in users[g.groupName]:
                group_list.append(g.groupName)
          
        if request.method == 'POST':
            form = addUserForm([], request.POST)
            if request.POST.get('username'):
                username = request.POST.get('username').strip()

                group_checked = False

                for g in group_list:
                    access = request.POST.get(g)

                    if access is not None:
                        theGroup = group.objects.get(groupName=g)
                        users = json.loads(theGroup.users)

                        if username not in users[g]:
                            users[g].append(username)
                            theGroup.users = json.dumps(users)
                            theGroup.save()
                            form = addUserForm(group_list)
                            return render(request, 'SecureWitness/addUser.html', {'form' : form, 'ingroup' : True, 'msg':'User was successfully added', 'admin':False })
                        else:
                            form = addUserForm(group_list)
                            return render(request, 'SecureWitness/addUser.html', {'form' : form, 'ingroup' : True, 'msg':'User is already in this group', 'admin':False })

                        group_checked = True

                if group_checked == False:
                    form = addUserForm(group_list)
                    return render(request, 'SecureWitness/addUser.html', {'msg': 'Please check at least 1 group.','form' : form, 'ingroup' : True, 'admin':False })
            else:
                form = addUserForm(group_list)
                return render(request, 'SecureWitness/addUser.html', {'form' : form, 'ingroup' : True, 'msg':'Please enter a username', 'admin':False })
        elif len(group_list) > 0:
            form = addUserForm(group_list)
            return render(request, 'SecureWitness/addUser.html', {'form' : form, 'ingroup' : True, 'admin':False })
        else:
            return HttpResponse(group_list)
            form = addUserForm(group_list)
            return render(request, 'SecureWitness/addUser.html', {'form' : form, 'ingroup':False, 'admin':False })
    else:
        return HttpResponse("You are not logged in")

def adminPage(request):
    if 'u' in request.session:
        if user.objects.get(username=request.session['u']).adminStatus == 1:
            return render(request, 'SecureWitness/adminPage.html')
        else:
            return HttpResponse("You are not an admin")
    else:
        return HttpResponse("You are not logged in")

def giveAdminAccess(request):
    if 'u' in request.session:
        if request.method == 'POST':
            form = GiveAdminAccessForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['username'].strip()

                try:
                    users = user.objects.get(username=name)
                    users.adminStatus = 1
                    users.save()
                    form = GiveAdminAccessForm()
                    return render(request, 'SecureWitness/giveAdminAccess.html', { 'form' : form, 'msg':'User was given admin access' })
                except:
                    form = GiveAdminAccessForm()
                    return render(request, 'SecureWitness/giveAdminAccess.html', { 'form' : form, 'msg':"User does not exist" })

            else:
                form = GiveAdminAccessForm()
                return render(request, 'SecureWitness/giveAdminAccess.html', { 'form' : form, 'msg':'Please enter a user.' })
        else:
            form = GiveAdminAccessForm()
            return render(request, 'SecureWitness/giveAdminAccess.html', { 'form' : form })
    else:
        return HttpResponse("You are not logged in")

def makeGroup(request):
    if 'u' in request.session:
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
        else:
            form = CreateGroupForm()
            return render(request, 'SecureWitness/createGroup.html', { 'form' : form } )
    else:
        return HttpResponse("You are not logged in")


def addUserToGroup(request):
    if 'u' in request.session:
        groups = group.objects.all()
        group_list = []
        for g in groups:
            users = json.loads(g.users)
            group_list.append(g.groupName)
         
        if len(group_list) == 0:
            return HttpResponse("There are no groups yet")

        if request.method == 'POST':
            form = addUserForm([], request.POST)
            if request.POST.get('username'):
                username = request.POST.get('username').strip()

                group_checked = False

                for g in group_list:
                    access = request.POST.get(g)

                    if access is not None:
                        theGroup = group.objects.get(groupName=g)
                        users = json.loads(theGroup.users)

                        if username not in users[g]:
                            users[g].append(username)
                            theGroup.users = json.dumps(users)
                            theGroup.save()
                            form = addUserForm(group_list)
                            return render(request, 'SecureWitness/addUser.html', {'msg': "User was successfully added.", 'form': form, 'ingroup': True, 'admin':True})
                        else:
                            form = addUserForm(group_list)
                            return render(request, 'SecureWitness/adduser.html', {'msg': "User is already in this group.", 'form' : form, 'ingroup': True, 'admin':True})

                        group_checked = True

                if group_checked == False:
                     form = addUserForm(group_list)
                     return render(request, 'SecureWitness/adduser.html', {'msg': "Please check at least one group.", 'form' : form, 'ingroup': True, 'admin':True})

            else:
                 form = addUserForm(group_list)
                 return render(request, 'SecureWitness/adduser.html', {'msg': "Please enter a username.", 'form' : form, 'ingroup': True, 'admin':True})

        else:
            form = addUserForm(group_list)
            return render(request, 'SecureWitness/addUser.html', {'form' : form, 'ingroup':True, 'admin':True })
    else:
        return HttpResponse("You are not logged in")

def changeUserSuspensionStatus(request):
    if 'u' in request.session:
        if request.method == 'POST':
            form = suspendUserForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username'].strip()
                try:
                    users = user.objects.get(username=username)
                    if 'suspend' in request.POST:
                        users.suspensionStatus = 1
                        users.save()
                        form = suspendUserForm()
                        return render(request, 'SecureWitness/changeUserSuspensionStatus.html', {'msg': "User was suspended.", 'form' : form})

                    else:
                        users.suspensionStatus = 0
                        users.save()
                        form = suspendUserForm()
                        return render(request, 'SecureWitness/changeUserSuspensionStatus.html', {'msg': "User was unsuspended.", 'form' : form})

                except:
                     form = suspendUserForm()
                     return render(request, 'SecureWitness/changeUserSuspensionStatus.html', {'msg': "User does not exist.", 'form' : form})

            else:
                 form = suspendUserForm()
                 return render(request, 'SecureWitness/changeUserSuspensionStatus.html', {'msg': "Please enter a username.", 'form' : form})

        else:
            form = suspendUserForm()
            return render(request, 'SecureWitness/changeUserSuspensionStatus.html', { 'form' : form })
    else:
        return HttpResponse("You are not logged in")

def deleteReport(request):
    if 'u' in request.session:
        if request.method == 'POST':
            form = deleteReportForm(request.POST)
            if form.is_valid():
                shortdesc = form.cleaned_data['shortdesc'].strip()
                try:
                    someReport = report.objects.get(shortdesc=shortdesc).delete()
                    form = deleteReportForm()
                    return render(request, 'SecureWitness/deleteReport.html', { 'form' : form, "msg":"Report has been deleted" })
                except:
                    form = deleteReportForm()
                    return render(request, 'SecureWitness/deleteReport.html', { 'form' : form, 'msg':"Report with given shortdesc does not exist" })
            else:
                form = deleteReportForm()
                return render(request, 'SecureWitness/deleteReport.html', { 'form' : form, 'msg':"Please enter a shortdesc" })
        else:
            form = deleteReportForm()
            return render(request, 'SecureWitness/deleteReport.html', { 'form' : form })
    else:
        return HttpResponse("You are not logged in")
