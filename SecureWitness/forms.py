from django import forms
from SecureWitness.models import user

class NameForm(forms.Form):
    your_name = forms.CharField(label='Search Criteria', max_length=100)

class GiveAdminAccessForm(forms.Form):
    username = forms.CharField(label='Username: ', max_length=100)