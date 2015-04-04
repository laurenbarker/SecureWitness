from django import forms
from SecureWitness.models import user
from django.utils.safestring import mark_safe

class NameForm(forms.Form):
    your_name = forms.CharField(label='Search Criteria', max_length = 100)

class GiveAdminAccessForm(forms.Form):
    username = forms.CharField(label='Username', max_length = 100)

class CreateGroupForm(forms.Form):
	groupName = forms.CharField(label='Group Name', max_length = 100)

class addUserForm(forms.Form):
	username = forms.CharField(label = 'Add User', max_length = 100)
	toGroup = forms.CharField(label = 'To Group' , max_length = 100)