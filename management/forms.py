from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm, ReadOnlyPasswordHashField

# from authentication.models import Announcement
from accounting.models import Subscriptionof
from .models import Announcement
#from django.contrib.auth.models import User

class SubscriptionAddForm(forms.ModelForm):
    """
    A Custom form for creating new users.
    """

    class Meta:
        model = Subscriptionof
        fields = ['subs_type','subs_of']


class AnnouncementAddForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['announcement_subject','announcement', 'announce_dismiss_date']
        announce_dismiss_date = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M:%S'])
