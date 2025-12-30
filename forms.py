from django import forms
from datetime import date
from django.contrib.auth.models import User
from .models import WLPublisher

class WlRuleForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput(), initial='add_rule')
    date_effective = forms.DateField(widget=forms.DateInput(
        attrs={'class': 'form-control', 'type': 'date'}), initial=date.today)
    percentage = forms.FloatField(required=False, initial='100', max_value=100, min_value=0,
                    widget=forms.NumberInput(attrs={'step': '0.1'}))

def get_user_choices(filters):
    return User.objects.filter(**filters).order_by('username').distinct()

class AssociatePublisherForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput(), initial='associate_user')
    user = forms.ModelChoiceField(queryset=get_user_choices( {'user_permissions__codename__contains':'publisher', 'is_active':True}))

class AssociateAdminForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput(), initial='associate_admin')
    user = forms.ModelChoiceField(queryset=get_user_choices( {'is_active':True}))

class WlConfigForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput(), initial='save_settings')
    name = forms.CharField(max_length=70)
    title = forms.CharField(max_length=50)
    pay_difference_to_id = forms.ModelChoiceField(queryset=get_user_choices({'is_active':True}))
    logo_icon = forms.CharField(max_length=20)
    primary_color = forms.CharField(max_length=7)
    secondary_color = forms.CharField(max_length=7)
    text_color = forms.CharField(max_length=7)

class WlPublisherSettingsForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput(), initial='update_publisher')
    bucket = forms.ChoiceField(choices=WLPublisher.BUCKET_TYPES)

class NewWhiteLabelConfiguration(forms.Form):
  name = forms.CharField(max_length=70)
  pay_difference_to_id = forms.ModelChoiceField(queryset=get_user_choices({'is_active':True}))
