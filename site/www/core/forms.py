from django import forms
from core.models import DATABASE_TYPES
from material import Layout


class DomainForm(forms.Form):
    domain_name = forms.CharField()
    domain_name.widget.attrs['class'] = 'form-control'

    app_type = forms.CharField()
    app_type.widget.attrs['class'] = 'form-control'

    layout = Layout('app_type', 'domain_name')


class LoginForm(forms.Form):

    username = forms.CharField(max_length=100)
    username.widget.attrs['class'] = 'form-control'
    username.widget.attrs['placeholder'] = 'Username'

    password = forms.CharField(max_length=100, widget=forms.PasswordInput())
    password.widget.attrs['class'] = 'form-control'
    password.widget.attrs['placeholder'] = 'Password'


class DatabaseForm(forms.Form):

    db_type = forms.ChoiceField(choices=DATABASE_TYPES, required=True)
    db_type.widget.attrs['class'] = 'form-control'
    db_type.widget.attrs['placeholder'] = 'Type'

    db_name = forms.CharField(max_length=100, required=True)
    db_name.widget.attrs['class'] = 'form-control'
    db_name.widget.attrs['placeholder'] = 'Database'

    db_user = forms.CharField(max_length=100, required=True)
    db_user.widget.attrs['class'] = 'form-control'
    db_user.widget.attrs['placeholder'] = 'Username'

    db_pass = forms.CharField(max_length=100, widget=forms.PasswordInput(), required=True)
    db_pass.widget.attrs['class'] = 'form-control'
    db_pass.widget.attrs['placeholder'] = 'Password'
