from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.conf import settings
import os
from django.core.mail import EmailMessage
from weasyprint import HTML,CSS
import tempfile

from authentication.models import CustomUser
from .forms import MeetingAddForm, MeetingAgendaAddForm, AttendanceForm, AgendaResponseForm
from .models import Meeting, Attendance, Agenda


# Create your views here.
@login_required
def meeting_home(request):
    all_meetings = Meeting.objects.all().order_by('-number')

    context = {
        'all_meetings' : all_meetings
    }
    return render(request, 'meeting/meeting_home.html', context)
@login_required
def meeting_add(request):
    if request.method == 'POST':
        m_form = MeetingAddForm(request.POST, request.FILES)
        unapprove_meeting = Meeting.objects.filter(final_approval=0)
        if unapprove_meeting:
            messages.error(request, "You can't add new meeting. One or more Meeting is still open")
        else:
            if m_form.is_valid():
                m_form.save()
                messages.success(request, 'Meeting Has been Created Successfully. Please add agenda related to the meeting')
                return redirect('meeting-home')
    else:
        m_form = MeetingAddForm()

    context = {
        'm_form' : m_form
    }
    return render(request, 'meeting/add_meeting.html', context)

@login_required
def agenda_add(request):
    if request.method == 'POST':
        a_form = MeetingAgendaAddForm(request.POST, request.FILES)
        if a_form.is_valid():
            a_form.save()

            messages.success(request, 'Meeting Agenda has been Created Successfully.')
            return redirect('meeting-home')
    else:
        a_form = MeetingAgendaAddForm()

    context = {
        'a_form' : a_form
    }
    return render(request, 'meeting/add_meeting_agenda.html', context)
@login_required
def attendance(request):
    if request.method == 'POST':
        at_form = AttendanceForm(request.POST, request.FILES)
        if at_form.is_valid():
            is_attended = Attendance.objects.filter(meeting_number=at_form.cleaned_data['meeting_number'], attendee =request.user)
            if is_attended:
                messages.error(request, 'You have given your attendance earlier.')
            else:
                attend = at_form.save()
                attend.refresh_from_db()
                attend.attendee = request.user
                attend.save()
                messages.success(request, 'Attendance Successful.')
                return redirect('meeting-home')
    else:
        at_form = AttendanceForm()

    context = {
        'at_form' : at_form
    }
    return render(request, 'meeting/attendance.html', context)

@login_required
def view_attendee(request, pk):
    attendees = Attendance.objects.filter(meeting_number=pk)
    if request.method == 'GET':
        return render(request, 'meeting/view_attendee.html', {
        'attendees': attendees,
        'meeting_number': pk
    })

@login_required
def view_agenda(request, pk):
    agendas = Agenda.objects.filter(meeting_number=pk).order_by('id')
    if request.method == 'GET':
        return render(request, 'meeting/view_agenda.html', {
        'agendas': agendas,
        'meeting_number': pk
    })

@login_required
def view_meeting(request,pk):
    meetings = Meeting.objects.get(number=pk)
    attendees = Attendance.objects.filter(meeting_number=pk)
    agendas = Agenda.objects.filter(meeting_number=pk)
    if request.method == 'GET':
        return render(request, 'meeting/view_meeting.html', {
        'meetings': meetings,
        'attendees': attendees,
        'agendas': agendas,
        'meeting_number': pk
    })    

@login_required
def close_meeting(request,pk):
    meeting = get_object_or_404(Meeting, number=pk)
    if request.user == meeting.chair:
        meeting.final_approval = 1
        meeting.save()
########## PDF Generation ############### 
    meetings = Meeting.objects.get(number=pk)
    attendees = Attendance.objects.filter(meeting_number=pk)
    agendas = Agenda.objects.filter(meeting_number=pk)
    current_site = get_current_site(request)
    context = {
        'meetings': meetings,
        'attendees': attendees,
        'agendas': agendas,
        'meeting_number': pk,
        'logo':'{}{}{}{}'.format('http://',current_site,settings.STATIC_URL,'image/uttaran-logo.PNG')
    }

    html_string = render_to_string('mail_format/meeting_download_template.html', context)
    html = HTML(string=html_string)
    filename = "Meeting_"+str(pk)+".pdf"
    css_url = os.path.join(settings.BASE_DIR, 'static/vendor/bootstrap/css/bootstrap.css')
    filename_2 = os.path.join(settings.MEDIA_ROOT)+'/pdfs/'+filename
    result = html.write_pdf(target=filename_2, stylesheets=[CSS(css_url)])

########## PDF Generation ############### 
    all_user = CustomUser.objects.filter(is_active=1)
    all_email = []
    for i in all_user:
        all_email.append(i.email)
    message = render_to_string('mail_format/meeting-close-sent-mail-template.html', {
        'meetings': meetings,
    }) 
    subject = 'Meeting ' + str(meetings.number) + 'has been closed'    
    email = EmailMessage(subject,message,settings.EMAIL_HOST_USER,all_email)
    file_to_be_sent = os.path.join(settings.BASE_DIR, filename_2)
    email.attach_file(file_to_be_sent)
    email.content_subtype = "html" 
    email.send()    
    return redirect('meeting-home')    
        

@login_required
def download_meeting(request,pk):
    meetings = Meeting.objects.get(number=pk)
    attendees = Attendance.objects.filter(meeting_number=pk)
    agendas = Agenda.objects.filter(meeting_number=pk)
    current_site = get_current_site(request)
    context = {
        'meetings': meetings,
        'attendees': attendees,
        'agendas': agendas,
        'meeting_number': pk,
        'logo':'{}{}{}{}'.format('http://',current_site,settings.STATIC_URL,'image/uttaran-logo.PNG')
    }

    html_string = render_to_string('mail_format/meeting_download_template.html', context)
    html = HTML(string=html_string)
    filename = "Meeting_"+str(pk)+".pdf"
    css_url = os.path.join(settings.BASE_DIR, 'static/vendor/bootstrap/css/bootstrap.css')
    filename_2 = os.path.join(settings.MEDIA_ROOT)+'/pdfs/'+filename

    result = html.write_pdf(target=filename_2, stylesheets=[CSS(css_url)])
    
    with open(filename_2, 'rb') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    return redirect('meeting-home')

@login_required
def response_add(request, pk):
    agenda = get_object_or_404(Agenda, pk=pk)
    if request.method == 'POST':
        if request.user == agenda.responsible_person:
            r_form = AgendaResponseForm(request.POST, request.FILES) 
            if r_form.is_valid():
                agenda.response_from_responsible_person = r_form.cleaned_data['response_from_responsible_person']
                agenda.response_date = timezone.now()
                agenda.save()
                messages.success(request, 'You response has been saved successfully.')
                return redirect('meeting-home')
        else: 
            messages.error(request, 'You have no permission to add response on this agenda.')
            return redirect('meeting-home')
    else:
        r_form = AgendaResponseForm()

    context = {
        'r_form' : r_form
    }
    return render(request, 'meeting/add_response.html', context)