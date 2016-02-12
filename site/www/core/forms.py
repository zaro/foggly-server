from django import forms
from core.models import APP_TYPES
from material import Layout

class DomainForm(forms.Form):
    domain_name = forms.CharField()
    domain_name.widget.attrs['class'] = 'form-control'

    app_type = forms.ChoiceField(choices=APP_TYPES)
    app_type.widget.attrs['class'] = 'form-control'

    layout = Layout('app_type', 'domain_name')


class LoginForm(forms.Form):

    username = forms.CharField(max_length=100)
    username.widget.attrs['class'] = 'form-control'
    username.widget.attrs['placeholder'] = 'Username'

    password = forms.CharField(max_length=100, widget=forms.PasswordInput())
    password.widget.attrs['class'] = 'form-control'
    password.widget.attrs['placeholder'] = 'Password'

