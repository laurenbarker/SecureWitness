from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render
from django.http import HttpResponseRedirect

from polls.models import report

from django import forms

class NameForm(forms.Form):
    your_name = forms.CharField(label='Search Criteria', max_length=100)

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
            list = report.objects.filter(shortdesc__contains=keyword)
            template = loader.get_template('polls/index.html')
            context = RequestContext(request, {
                  'latest_question_list': list,
            })
            return HttpResponse(template.render(context))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()
    return render(request, 'polls/search.html', {'form': form})

def result(request):

    latest_question_list = report.objects.order_by('timestamp')
    template = loader.get_template('polls/index.html')
    context = RequestContext(request, {
        'latest_question_list': latest_question_list,
    })
    return HttpResponse(template.render(context))