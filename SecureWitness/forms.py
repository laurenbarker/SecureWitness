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

    def __init__(self,group_list = [], Post=""):
        super(addUserForm, self).__init__()
        for group in group_list:
            self.fields[group] = forms.BooleanField(required=False)

class suspendUserForm(forms.Form):
    username = forms.CharField(label='Username', max_length = 100)

class deleteReportForm(forms.Form):
	shortdesc = forms.CharField(label='Shortdesc', max_length = 100)