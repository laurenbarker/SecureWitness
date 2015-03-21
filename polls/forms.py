from django import forms

class NameForm(forms.Form):
    your_name = forms.CharField(label='Search Criteria', max_length=100)