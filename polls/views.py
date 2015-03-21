from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from polls.models import report,user
import time
from django import forms

class NameForm(forms.Form):
    your_name = forms.CharField(label='Search Criteria', max_length=100)

class UploadFileForm(forms.Form):
    shortdesc = forms.CharField(max_length=50)
    longdesc = forms.CharField(max_length=300)
    location = forms.CharField(max_length=50)
    incident_date = forms.DateField()
    keywords = forms.CharField(max_length=50)
    private = forms.BooleanField()
    file = forms.FileField()


def index(request):
    latest_question_list = report.objects.order_by('timestamp')
    template = loader.get_template('polls/index.html')
    context = RequestContext(request, {
        'latest_question_list': latest_question_list,
    })
    return HttpResponse(template.render(context))

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
            template = loader.get_template('polls/index.html')
            context = RequestContext(request, {
                  'latest_question_list': list,
            })
            return HttpResponse(template.render(context))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()
    return render(request, 'polls/search.html', {'form': form})

def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            short = form.cleaned_data['shortdesc']
            long = form.cleaned_data['longdesc']
            loc = form.cleaned_data['location']
            inc = form.cleaned_data['incident_date']
            key = form.cleaned_data['keywords']
            priv = form.cleaned_data['private']
            f = request.FILES['file']
            #u = user(username = 'test', password = '1234')
            rep = report( shortdesc = short, longdesc = long, location = loc, incident_date = inc, keywords = key, private = priv, file = f)
            rep.save()
            return HttpResponse("added successfully")
    else:
        form = UploadFileForm()
    return render(request,'polls/upload.html', {'form': form})