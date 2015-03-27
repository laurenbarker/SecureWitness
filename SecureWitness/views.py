from django.http import HttpResponse
# from django.template import RequestContext, loader
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from SecureWitness.models import report,user
from SecureWitness.forms import GiveAdminAccessForm
import time

#put forms in forms.py later
from django import forms

class NameForm(forms.Form):
    your_name = forms.CharField(label='Search Criteria', max_length=100)

class UploadFileForm(forms.Form):
    shortdesc = forms.CharField(max_length=50)
    longdesc = forms.CharField(max_length=300)
    location = forms.CharField(max_length=50, required=False)
    incident_date = forms.DateField(required=False)
    keywords = forms.CharField(max_length=50, required=False)
    private = forms.BooleanField(required=False)
    file = forms.FileField(required=False)

def index(request):
    report_list = report.objects.order_by('timestamp')
    template = loader.get_template('SecureWitness/index.html')
    context = RequestContext(request, {
        'report_list': report_list,
    })
    return HttpResponse(template.render(context))

#search
def search(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            keyword = form.cleaned_data['your_name']
            keyword = keyword.split()
            list = []
            for word in keyword:
                list.extend(report.objects.filter(shortdesc__contains=word))
            list = set(list)
            template = loader.get_template('SecureWitness/index.html')
            context = RequestContext(request, {
                  'latest_question_list': list,
            })
            return HttpResponse(template.render(context))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()
    return render(request, 'SecureWitness/search.html', {'form': form})

#upload reports
def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            short = form.cleaned_data['shortdesc']
            long = form.cleaned_data['longdesc']
            if form.cleaned_data['location'] is None:
                loc = None
            else:
                loc = form.cleaned_data['location']
            if form.cleaned_data['incident_date'] is None:
                inc = None
            else:
                inc = form.cleaned_data['incident_date']
            if form.cleaned_data['keywords'] is None:
                key = None
            else:
                key = form.cleaned_data['keywords']
            if form.cleaned_data['private'] is None:
                priv = False
            else:
                priv = form.cleaned_data['private']
            if request.FILES.get('file') is None:
                f = None
            else:
                f = request.FILES['file']
            #Once login is finished, get current logged in user
            name = "test"
            u = user.objects.filter(username=name)[0]
            rep = report(author = u, shortdesc = short, longdesc = long, location = loc, incident_date = inc, keywords = key, private = priv, file = f)
            rep.save()
            return HttpResponse("added successfully")
    else:
        form = UploadFileForm()
    return render(request,'SecureWitness/upload.html', {'form': form})

def adminPage(request):
    if request.method == 'POST':
        form = GiveAdminAccessForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['username']

            try: 
                users = user.objects.get(username=name)
                users.adminStatus = 1
                users.save()
                return HttpResponse("User was given admin acces")
            except:
                return HttpResponse("User does not exist")
    else:
        form = GiveAdminAccessForm()
        return render(request, 'SecureWitness/adminPage.html', { 'form' : form })



