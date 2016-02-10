from django import forms
from core.models import APP_TYPES
from material import Layout

class DomainForm(forms.Form):
    domain_name = forms.CharField()
    domain_name.widget.attrs['class'] = 'form-control'
    app_type = forms.ChoiceField(choices=APP_TYPES)
    app_type.widget.attrs['class'] = 'form-control'

    layout = Layout('app_type', 'domain_name')
