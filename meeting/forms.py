from django.contrib.auth import get_user_model
from django import forms

from .models import Meeting, Agenda, Attendance
from authentication.models import CustomUser


#from django.contrib.auth.models import User


class MeetingAddForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MeetingAddForm, self).__init__(*args, **kwargs)
        users = CustomUser.objects.all()
        meeting_object = Meeting.objects.all().last()
        if meeting_object:
            next_meeting_number = meeting_object.number + 1
        else:
            next_meeting_number = 1

        self.fields['number'].initial = next_meeting_number
        self.fields['number'].widget.attrs['readonly'] = True
        self.fields['chair'].choices = [(user.pk, user.get_full_name()) for user in users]
        self.fields['minute_taker'].choices = [(user.pk, user.get_full_name()) for user in users]
    class Meta:
        model = Meeting
        fields = ['number', 'date', 'chair', 'place', 'mtype', 'minute_taker']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        # 

class MeetingAgendaAddForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MeetingAgendaAddForm, self).__init__(*args, **kwargs)
        meetings = Meeting.objects.filter(final_approval=0)
        self.fields['meeting_number'].choices = [(meeting.pk, meeting.pk) for meeting in meetings]
        users = CustomUser.objects.all()
        self.fields['responsible_person'].choices = [(user.pk, user.get_full_name()) for user in users]
        self.fields['topic_initiator'].choices = [(user.pk, user.get_full_name()) for user in users]


    class Meta:

        model = Agenda
        fields = ['meeting_number', 'topic', 'topic_initiator', 'discussion', 'action', 'responsible_person', 'deadline']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class AttendanceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)
        users = Meeting.objects.filter(final_approval=0)
        self.fields['meeting_number'].choices = [(user.pk, user.pk) for user in users]
    class Meta:
        model = Attendance
        fields = ['meeting_number']


class AgendaResponseForm(forms.ModelForm):
    class Meta:
        model = Agenda
        fields = ['response_from_responsible_person']