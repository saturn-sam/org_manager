from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from authentication.models import CustomUser

from .models import Deposite, Earning, Expenditure

#from django.contrib.auth.models import User

class DepositForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DepositForm, self).__init__(*args, **kwargs)
        users = CustomUser.objects.all()
        self.fields['member_name'].choices = [(user.pk, user.get_full_name()) for user in users]
    class Meta:
        model = Deposite
        fields = ['member_name','sub_of', 'amount', 'bank_ref_num', 'recipt_image']

class EarningForm(forms.ModelForm):
    class Meta:
        model = Earning
        fields = ['earning_source','description', 'amount', 'document_image']

class DateInput(forms.DateInput):
    input_type = 'date'

class ExpenditureForm(forms.ModelForm):
    class Meta:
        model = Expenditure
        fields = ['expenditure_source', 'expenditure_type', 'description', 'amount', 'expenditure_date', 'supporting_document']
        widgets = {
            'expenditure_date': DateInput(),
        }

class AllEarningReportForm(forms.ModelForm):
    class Meta:
        model = Earning
        fields = ['earning_source']
    def __init__(self, *args, **kargs):
        super(AllEarningReportForm, self).__init__(*args, **kargs)
        
        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field and isinstance(field , forms.TypedChoiceField):
                field.choices = field.choices[1:]
    

class AllExpTypeReportForm(forms.ModelForm):
    class Meta:
        model = Expenditure
        fields = ['expenditure_type']
    def __init__(self, *args, **kargs):
        super(AllExpTypeReportForm, self).__init__(*args, **kargs)
        
        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field and isinstance(field , forms.TypedChoiceField):
                field.choices = field.choices[1:]

class DateRangeForm(forms.Form):
    start_date = forms.DateTimeField(input_formats=['%d/%m/%Y'])
    end_date = forms.DateTimeField(input_formats=['%d/%m/%Y'])

    def clean(self):
        cleaned_data = super(DateRangeForm, self).clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if not start_date or not end_date:
            raise forms.ValidationError('Please select date range!')

