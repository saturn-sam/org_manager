from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.forms import DateTimeField

from .models import Profile
#from django.contrib.auth.models import User

class UserAdminCreationForm(UserCreationForm):
    """
    A Custom form for creating new users.
    """

    class Meta:
        model = get_user_model()
        fields = ['email', 'first_name', 'last_name']



class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = get_user_model()
    
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    #disabled_fields = ('email',)

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = True
        self.fields['email'].disabled = True
    
    class Meta:
        model = User
        fields = ['email', 'first_name','last_name']
        


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image','father_or_husband_name', 'mother_name', 'per_vill', 'per_po','per_ps','per_dist','pre_vill','pre_po','pre_ps','pre_dist','dob','phone','blood_group','nid','passport','tin','driving_license','profession','religion','nominee_image','nominee_name','nominee_father_or_husband_name','nominee_mother_name','nominee_per_vill','nominee_per_po','nominee_per_ps','nominee_per_dist','nominee_pre_vill','nominee_pre_po','nominee_pre_ps','nominee_pre_dist']

