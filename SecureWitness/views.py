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
            return HttpResponse('Authentication succeeded.' + '\n')
    else:
        return HttpResponse("unsuccessful authentication")

@csrf_exempt
def viewReports_decrypt(request):
    # get reports for user
    u = request.POST.get('username')
    pw = request.POST.get('password')
    # check and see if that user exists
    users = user.objects.filter(username=u).filter(password=pw)
    if(len(users) <= 0):
        return HttpResponse("unsuccessful authentication")

    u = user.objects.filter(username=u)[0]
    report_list = report.objects.filter(Q(author=u)  | Q(private=False))

    groups = group.objects.all()
    group_list = []
    for g in groups:
        users = json.loads(g.users)
        if u in users[g.groupName]:
            group_list.append(g.groupName)

    report_names = []

    for g in group_list:
        all_reports = report.objects.all()
        for a_report in all_reports:
            if g in a_report.group:
                #GET REPORT BY UNIQUE IDENTIFIERS
                report_names.append(a_report.id)

        group_report_list = report.objects.filter(id__in=report_names)

        report_list = report_list | group_report_list
  
    grp = ""
    for g in group_list:
        grp = grp + str(g)

    #ob_list = report.objects.filter(reduce(lambda x, y: x | y, [Q(name__contains=word) for word in group_list]))
    return HttpResponse(str(list((report_list))) + '\n')
    #return HttpResponse(groups)

@csrf_exempt
def viewFiles_decrypt(request):
    # get reports for user
    u = request.POST.get('username')
    pw = request.POST.get('password')
    rpt = request.POST.get('report')
    # check and see if that user exists
    users = user.objects.filter(username=u).filter(password=pw)
    if(len(users) <= 0):
        return HttpResponse("unsuccessful authentication")

    u = user.objects.filter(username=u)[0]
    report_list = report.objects.filter(Q(author=u)  | Q(private=False))
    groups = group.objects.all()
    group_list = []
    for g in groups:
        users = json.loads(g.users)
        if u in users[g.groupName]:
            group_list.append(g.groupName)

    report_names = []

    for g in group_list:
        all_reports = report.objects.all()
        for a_report in all_reports:
            if g in a_report.group:
                #GET REPORT BY UNIQUE IDENTIFIERS
                report_names.append(a_report.id)

        group_report_list = report.objects.filter(id__in=report_names)

        report_list = report_list | group_report_list
    #return HttpResponse('this works')
    rp = ""
    frp = ""
    for r in report_list:
        #rp += str(r)
        if r.id == int(rpt):
            rp = 'found'
            frp = r
            break

    if rp != 'found':
        return HttpResponse('Report not found.')

    #for reports in report_list:
        #if str(reports) == str(frp):

    if r.file:
        r.file.name = r.file.name.split('staticfiles')[1][1:]
    frp = r.file.name
    shrt = r.shortdesc
    lng = r.longdesc
    loc = r.location
    kwds = r.keywords
    date = r.incident_date
    auth = r.author


    
    return HttpResponse(str(rpt) + '\t' + str(auth) + '\t' + str(shrt) + '\t' + str(lng) + '\t' + str(loc) + '\t' + str(kwds) + '\t' + str(date) + '\t' + str(frp) + '\n')
    #return HttpResponse(groups)

@csrf_exempt
def uploaded_key(request):
    # get reports for user
    u = request.POST.get('username')
    pw = request.POST.get('password')
    rpt = request.POST.get('report')
    fn = request.POST.get('file')
    # check and see if that user exists
    users = user.objects.filter(username=u).filter(password=pw)
    if(len(users) <= 0):
        return HttpResponse("unsuccessful authentication")

    u = user.objects.filter(username=u)[0]
    report_list = report.objects.filter(Q(author=u)  | Q(private=False))

    groups = group.objects.all()
    group_list = []
    for g in groups:
        users = json.loads(g.users)
        if u in users[g.groupName]:
            group_list.append(g.groupName)

    report_names = []

    for g in group_list:
        all_reports = report.objects.all()
        for a_report in all_reports:
            if g in a_report.group:
                #GET REPORT BY UNIQUE IDENTIFIERS
                report_names.append(a_report.id)

        group_report_list = report.objects.filter(shortdesc__in=report_names)

        report_list = report_list | group_report_list
  
    rp = ""
    frp = ""
    for r in report_list:
        #rp += str(r)
        if r.id == int(rpt):
            rp = 'found'
            frp = r
            break

    if rp != 'found':
        return HttpResponse('Report not found.')

    for reports in report_list:
        if str(reports) == str(frp):
            reports.file.name = reports.file.name.split('staticfiles')[1][1:]
            frp = reports.file.name
            if str(frp) != fn:
                return HttpResponse("Invalid file name.")
            ky = reports.key
            break

    
    return HttpResponse(str(ky))
    #return HttpResponse("In progress...")

@csrf_exempt
def uploaded_file_decrypt(request, fn):
    # get reports for user
    
    path2 = os.path.join(settings.STATIC_ROOT, fn)
    dest = open(path2, 'rb')
    response = HttpResponse(dest, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % fn
    # response['X-Sendfile'] = path2

    
    return response
    #return HttpResponse("In progress...")

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


        for reports in report_list:
            if reports.file:
                reports.file.name = reports.file.name.split('staticfiles')[1][1:]
        return render(request, 'SecureWitness/index.html', {
            'report_list': report_list,
            'user' : request.session['u'],
            'folder_list' : folders,
            'group_list' : group_list,
        })
    else:
        return render(request, 'SecureWitness/login.html', {'form' : loginForm()})

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

            for reports in desclist:
                if reports.file:
                    reports.file.name = reports.file.name.split('staticfiles')[1][1:]
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
            name = request.session['u']
            u = user.objects.filter(username=name)[0]
            fold = request.POST.get('folder')
            if not fold:
                fold = None
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

            rep = report(author = u, shortdesc = short, longdesc = long, location = loc, incident_date = date, keywords = kwds, private = priv, folder = fold)
            rep.save()
            f = request.FILES.get('file')
            if f:
                # public/private key pair
                random_generator = Random.new().read
                key = RSA.generate(1024, random_generator)
                pkey = key.exportKey('PEM')

                # encrypt
                public_key = key.publickey()
                # change

                newName = f.name + "_enc" + str(rep.id)

                path2 = os.path.join(settings.STATIC_ROOT, newName)
                #path2 = os.path.join(settings.STATIC_ROOT, newName)
                #path = os.path.join('staticfiles', newName)
                myf = open(path2, "w+b")
                testing = 0
                #for chunk in f.chunks():
                    #enc_data = public_key.encrypt(chunk, 32)
                    #myf.write(enc_data[0])
                    #testing+=1
                size = f.size
                for x in range(0,size,128):
                    enc_data = public_key.encrypt(f.read(128), 32)
                    myf.write(enc_data[0])
                f = path2
            else:
                pkey = ""
            rep.key = pkey
            rep.file = f
            #rep = report(author = u, shortdesc = short, longdesc = long, location = loc, incident_date = date, keywords = kwds, private = priv, file = f, folder = fold, key = pkey)
            rep.group = json.dumps(group_access)
            #rep.f = myf
            rep.save()
            #get groups user is in
            group_list = []
            groups = group.objects.all()
            for g in groups:
                users = json.loads(g.users)
                if request.session['u'] in users[g.groupName]:
                    group_list.append(g.groupName)
            form = UploadFileForm(group_list)
            return render(request,'SecureWitness/upload.html', {'form': form, 'msg': "Report was submitted successfully"})
        else:
            return render(request,'SecureWitness/upload.html', {'form': form, 'msg':'Short description and long description are required.'})
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
        return render(request, 'SecureWitness/login.html', {'form' : loginForm()})

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

        for reports in report_list:
            if reports.file:
                reports.file.name = reports.file.name.split('staticfiles')[1][1:]
        context = RequestContext(request, {
                'report_list': report_list,
                'user' : request.session['u'],
                'folder_name' : folder
        })
        return HttpResponse(template.render(context))
    else:
        return render(request, 'SecureWitness/login.html', {'form' : loginForm()})

def viewReport(request, number=""):
    if 'u' in request.session:
        if request.method == 'POST':
            if request.POST.get('del'):

                #Delete file from directory
                report_file = report.objects.filter(id=number)
                for r in report_file:
                    if r.file:
                        try: 
                            os.remove(r.file.name)                            
                        except:
                            msg = 'No file was found'

                report_list = report.objects.filter(id=number).delete()
                template = loader.get_template('SecureWitness/viewReport.html')
                context = RequestContext(request, {
                   'user' : request.session['u'],
                })
                return HttpResponse(template.render(context))
            else:

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
                report_list = report.objects.filter(id=number)[0]
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
                if report_list.file:
                    report_list.file.name = report_list.file.name.split('staticfiles')[1][1:]
                return HttpResponseRedirect(number)
        else:
            name = request.session['u']
            u = user.objects.filter(username=name)[0]
            report_list = report.objects.get(id=number)
            template = loader.get_template('SecureWitness/viewReport.html/')
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

            if report_list.file:
                report_list.file.name = report_list.file.name.split('staticfiles')[1][1:]

            context = RequestContext(request, {
                    'report': report_list,
                    'user' : request.session['u'],
                    'form' : form,
                    'groups' : group_dict
            })
            return HttpResponse(template.render(context))
    else:
        return render(request, 'SecureWitness/login.html', {'form' : loginForm()})

def viewAvailableReports(request):
    if 'u' in request.session:
        name = request.session['u']
        u = user.objects.filter(username=name)[0]
        report_list = report.objects.filter(Q(author=u)  | Q(private=False))

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
                    report_names.append(a_report.id)

        group_report_list = report.objects.filter(id__in=report_names)

        report_list = report_list | group_report_list

        for reports in report_list:
            if reports.file:
                reports.file.name = reports.file.name.split('staticfiles')[1][1:]

        return render(request, 'SecureWitness/availableReports.html', {
            'report_list': report_list,
            'user' : request.session['u'],
            'group_list' : group_list,
        })
    else:
        return render(request, 'SecureWitness/login.html', {'form' : loginForm()})

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
        return render(request, 'SecureWitness/login.html', {'form' : loginForm()})

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
            return render(request, 'SecureWitness/login.html', {'form' : loginForm()})

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

                        if username not in users[g] and user.objects.filter(username=username).count() > 0:
                            users[g].append(username)
                            theGroup.users = json.dumps(users)
                            theGroup.save()
                            form = addUserForm(group_list)
                            return render(request, 'SecureWitness/addUser.html', {'form' : form, 'ingroup' : True, 'msg':'User was successfully added', 'admin':False })
                        elif username in users[g]:
                            form = addUserForm(group_list)
                            return render(request, 'SecureWitness/addUser.html', {'form' : form, 'ingroup' : True, 'msg':'User is already in this group', 'admin':False })
                        else:
                            form = addUserForm(group_list)
                            return render(request, 'SecureWitness/addUser.html', {'form' : form, 'ingroup' : True, 'msg':'Username does not exist', 'admin':False })
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
            return render(request,'SecureWitness/userhome.html', { 'ingroup':False, 'admin':False, 'msg':"You are not a member of any groups." })
    else:
            return render(request, 'SecureWitness/login.html', {'form' : loginForm()})

def adminPage(request):
    if 'u' in request.session:
        if user.objects.get(username=request.session['u']).adminStatus == 1:
            return render(request, 'SecureWitness/adminPage.html')
        else:
            return HttpResponse("You are not an admin")
    else:
            return render(request, 'SecureWitness/login.html', {'form' : loginForm()})

def giveAdminAccess(request):
    if 'u' in request.session:
        if request.method == 'POST':
            form = GiveAdminAccessForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['username'].strip()

                try:
                    users = user.objects.get(username=name)
                    if users.adminStatus == 0: 
                        users.adminStatus = 1
                        users.save()
                        form = GiveAdminAccessForm()
                        return render(request, 'SecureWitness/giveAdminAccess.html', { 'form' : form, 'msg':'User was given admin access' })
                    else:
                        return render(request, 'SecureWitness/giveAdminAccess.html', { 'form' : form, 'msg' : "User already has admin access"})
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
            return render(request, 'SecureWitness/login.html', {'form' : loginForm()})

def makeGroup(request):
    if 'u' in request.session:
        if request.method == 'POST':
            form = CreateGroupForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['groupName']
                if group.objects.filter(groupName = name).exists():
                    form = CreateGroupForm()
                    return render(request, 'SecureWitness/createGroup.html', { 'form' : form, 'msg':'Group already exists' } )
                else:
                    users = {}
                    users[name] = []
                    myGroup = group(groupName = name, users = json.dumps(users))
                    myGroup.save()
                    form = CreateGroupForm()
                    return render(request, 'SecureWitness/createGroup.html', { 'form' : form, 'msg':'Group was successfully created!' } )
        else:
            form = CreateGroupForm()
            return render(request, 'SecureWitness/createGroup.html', { 'form' : form } )
    else:
            return render(request, 'SecureWitness/login.html', {'form' : loginForm()})


def addUserToGroup(request):
    if 'u' in request.session:
        groups = group.objects.all()
        group_list = []
        for g in groups:
            users = json.loads(g.users)
            group_list.append(g.groupName)
         
        if len(group_list) == 0:
            return render(request, 'SecureWitness/adminPage.html', {'msg':'There are no groups yet.'})

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
            return render(request, 'SecureWitness/login.html', {'form' : loginForm()})

def changeUserSuspensionStatus(request):
    if 'u' in request.session:
        if request.method == 'POST':
            form = suspendUserForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username'].strip()
                try:
                    users = user.objects.get(username=username)
                    if 'suspend' in request.POST:
                        if users.suspensionStatus == 0:
                            users.suspensionStatus = 1
                            users.save()
                            form = suspendUserForm()
                            return render(request, 'SecureWitness/changeUserSuspensionStatus.html', {'msg': "User was suspended.", 'form' : form})
                        else:
                            form = suspendUserForm
                            return render(request, 'SecureWitness/changeUserSuspensionStatus.html', {'msg': "User is already suspended.", 'form' : form})
                    else:
                        if users.suspensionStatus == 1:
                            users.suspensionStatus = 0
                            users.save()
                            form = suspendUserForm()
                            return render(request, 'SecureWitness/changeUserSuspensionStatus.html', {'msg': "User was unsuspended.", 'form' : form})
                        else:
                            form = suspendUserForm()
                            return render(request, 'SecureWitness/changeUserSuspensionStatus.html', {'msg': "User is not suspended.", 'form' : form})

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
            return render(request, 'SecureWitness/login.html', {'form' : loginForm()})

def deleteReport(request, number=''):
    if 'u' in request.session:
        if request.method == 'POST':
            if request.POST.get('del'):

                report_file = report.objects.filter(id=number)
                for r in report_file:
                    if r.file:
                        try: 
                            os.remove(r.file.name)                            
                        except:
                            msg = 'No file was found'

                report_list = report.objects.filter(id=number).delete()
                template = loader.get_template('SecureWitness/deleteReport.html')

            form = deleteReportForm(request.POST)
            report_list = report.objects.all()

            form = deleteReportForm()
            return render(request, 'SecureWitness/deleteReport.html', { 'form' : form, 'report_list' : report_list })
        else:
            form = deleteReportForm(request.POST)
            report_list = report.objects.all()

            form = deleteReportForm()
            return render(request, 'SecureWitness/deleteReport.html', { 'form' : form, 'report_list' : report_list })
    else:
            return render(request, 'SecureWitness/login.html', {'form' : loginForm()})
