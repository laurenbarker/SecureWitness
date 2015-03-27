from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from SecureWitness.models import report,user
import time

#put forms in forms.py later
from django import forms
class loginForm(forms.Form):
    username =  forms.CharField(max_length=50)
    password =  forms.CharField(max_length=50)

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
#work on login page
def login(request):
        # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = loginForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            user = form.cleaned_data['username']
            pw = form.cleaned_data['password']

           # return HttpResponse(template.render(context))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()
    return render(request, 'SecureWitness/search.html', {'form': form})


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
            loc = request.POST.get('location')
            if form.cleaned_data['incident_date'] is None:
                inc = None
            else:
                inc = request.POST.get('incident_date')
            key = request.POST.get('keywords')
            priv = request.POST.get('private')
            if priv is None:
                priv = False
            f = request.FILES.get('file')
            #Once login is finished, get current logged in user
            name = "test"
            u = user.objects.filter(username=name)[0]
            rep = report(author = u, shortdesc = short, longdesc = long, location = loc, incident_date = inc, keywords = key, private = priv, file = f)
            rep.save()
            return HttpResponse("added successfully")
    else:
        form = UploadFileForm()
    return render(request,'SecureWitness/upload.html', {'form': form})