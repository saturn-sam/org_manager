from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.conf import settings
import os
import logging
from django.utils import timezone

from authentication.models import CustomUser, Profile
from .forms import SubscriptionAddForm, AnnouncementAddForm
from accounting.models import Subscriptionof
from .models import Announcement
# Create your views here.

logger = logging.getLogger(__name__)


@login_required
def view_all_members(request):

    all_members = CustomUser.objects.all()
    context = {
        'all_members' : all_members,
    }

    return render(request, 'management/view_all_member.html', context)

@login_required
def view_user_profile(request,pk): 
    if request.user.is_staff:
        user_view = get_object_or_404(CustomUser, id=pk)
        from datetime import date
        age = int((date.today() - user_view.profile.dob).days/365.2425)
        if request.method == 'GET':
            return render(request, 'management/profile-view-to-admin.html', {
                'user_view': user_view,
                'age': age
            })
    else:
        messages.error(request, 'Your are not allowed to access this page!')
        return redirect('home')

@login_required
def disable_member(request,pk):
    if request.user.is_staff:
        user_s = get_object_or_404(CustomUser, id=pk)

        if request.method == 'POST':
            if not user_s.is_superuser:
                user_s.is_active = 0
                user_s.profile.disable_status = 1
                user_s.save()
                return JsonResponse({"status":"success","message": f"Selected User has been Deactivated Successfully!"})
            else:
                return JsonResponse({"status":"error","message": f"Your are not allowed to disable a Super Admin!"})

    else:
        return JsonResponse({"status":"error","message": f"You are unauthorized to access this page!"})

@login_required
def enable_member(request,pk):
    if request.user.is_staff:
        user_s = get_object_or_404(CustomUser, id=pk)
        if request.method == 'POST':
            if not user_s.last_login:
                user_s.is_active = 1
                user_s.profile.disable_status = 0
                user_s.save()
                # logger.error('Account of ' + user_s.get_full_name() + ' has been enabled by ' + request.user.get_full_name())
                current_site = get_current_site(request)
                subject = 'Uttaran member account confirmed'

                message = render_to_string('mail_format/account_request.html', {
                    'user_s': user_s,
                    'domain': current_site.domain,
                })       
                user_s.email_user(subject, '', html_message=message)  
                
                # logger.error('Account activation Mail sent to ' + user_s.get_full_name())       
                return JsonResponse({"status":"success","message": f"User has been activated successfully!"})
            else:
                user_s.is_active = 1
                user_s.profile.disable_status = 0
                user_s.save()
                # logger.error('Account of ' + user_s.get_full_name() + ' has been enabled by ' + request.user.get_full_name())
                return JsonResponse({"status":"success","message": f"User has been activated successfully!"})          

    else:
        return JsonResponse({"status":"error","message": f"You are unauthorized to access this page!"})

def make_admin(request, pk):
    if request.user.is_staff:
        user_s = get_object_or_404(CustomUser, id=pk)

        if request.method == 'POST':
            CustomUser.objects.filter(id=pk).update(is_staff=1)
            # logger.error(request.user.get_full_name() + ' make ' + user_s.get_full_name() +' admin')
            return JsonResponse({"status":"success","message": f"User {user_s.get_full_name()} marked as admin successfully!"})                    

    else:
        return JsonResponse({"status":"error","message": f"You are unauthorized to access this page!"})   

def remove_admin(request, pk):
    if request.user.is_staff:
        user_s = get_object_or_404(CustomUser, id=pk)

        if request.method == 'POST':
            CustomUser.objects.filter(id=pk).update(is_staff=0)
            # logger.error(request.user.get_full_name() + ' make ' + user_s.get_full_name() +' member')
            return JsonResponse({"status":"success","message": f"User {user_s.get_full_name()} marked as member successfully!"})             

    else:
        return JsonResponse({"status":"error","message": f"You are unauthorized to access this page!"})

def add_subscription(request):
    if request.user.is_staff:
        if request.method == 'POST':
            form_s = SubscriptionAddForm(request.POST)
            if form_s.is_valid():
                if form_s.cleaned_data['subs_type'] == 'Monthly':
                    subs_input = form_s.cleaned_data['subs_of']
                    if Subscriptionof.objects.filter(subs_of=subs_input).exists():
                        messages.error(request, 'This Subscription already added!')
                    else:
                        subs_input_list = subs_input.split()
                        if len(subs_input_list) != 2:
                            messages.error(request, 'Please Insert Subscription Month with Correct Pattern!')
                        else: 
                            months = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']
                            if subs_input_list[0].upper() in months and subs_input_list[1][:2] == '20':
                                subs = form_s.save()
                                subs.refresh_from_db()
                                subs.insert_by = request.user
                                subs.save()
                                
                                messages.success(request, 'Subscription has been added successfully!')
                                
                            else:
                                messages.error(request, 'Please Insert Subscription Month with Correct Pattern!')

                else:
                    subs = form_s.save()
                    subs.refresh_from_db()
                    subs.insert_by = request.user
                    subs.save()
                    messages.success(request, 'Subscription has been added successfully!')               

        form_s = SubscriptionAddForm()
        context={
            'form_s':form_s
        }
        return render(request, 'management/add_subs.html',context)

    else:
        messages.error(request, 'Your are not allowed to access this page!')
        return redirect('home')   


@login_required
def add_announcement(request):     
    if request.user.is_staff:
        if request.method == 'POST':
            form_a = AnnouncementAddForm(request.POST)

            if form_a.is_valid():
                ann = form_a.save()
                ann.refresh_from_db()
                ann.announcer = request.user
                ann.save()
                messages.success(request, 'Announcement has been added successfully!')
                all_user = CustomUser.objects.filter(is_active=1)
                all_email = []
                for i in all_user:
                    all_email.append(i.email)
                ann_sub = form_a.cleaned_data['announcement_subject']
                ann_body = form_a.cleaned_data['announcement']
                message = render_to_string('mail_format/announcement-sent-mail-template.html', {
                            'ann_sub': ann_sub,
                            'ann_body': ann_body,
                        }) 
                subject = 'New Announcement- "' + ann_sub +'"'
                email = EmailMessage(subject,message,settings.EMAIL_HOST_USER,all_email)
                email.content_subtype = "html" 
                email.send()
        form_a = AnnouncementAddForm()
        context={
            'form_a':form_a
        }
        return render(request, 'management/add_announcement.html',context)

    else:
        messages.error(request, 'Your are not allowed to access this page!')
        return redirect('home') 

@login_required
def view_announcement(request):    
    if request.user.is_staff:
        ann = Announcement.objects.all()
        context={
            'ann':ann,
            'time':timezone.now(),
        }

        return render(request, 'management/view_announcement.html',context)

    else:
        messages.error(request, 'Your are not allowed to access this page!')
        return redirect('home') 

@login_required
def unpublish_announcement(request,pk):
    if request.user.is_staff:
        if request.method == 'POST':
            try:
                Announcement.objects.filter(id=pk).update(unpublish_status=True, unpublish_by=request.user, unpublish_date=timezone.now())
            except:
                return JsonResponse({"status":"error","message": f"Announcement did not archived successfully. Something goes wrong!"})
            else:
                return JsonResponse({"status":"success","message": f"Announcement have been archived successfully!"})
    else:
        return JsonResponse({"status":"error","message": f"You are unauthorized to access this page!"})

@login_required
def publish_announcement(request,pk):
    if request.user.is_staff:
        if request.method == 'POST':
            try:
                Announcement.objects.filter(id=pk).update(unpublish_status=False, unpublish_by=request.user, unpublish_date=timezone.now())
            except:
                return JsonResponse({"status":"error","message": f"Announcement did not activated successfully. Something goes wrong!"})
            else:
                return JsonResponse({"status":"success","message": f"Announcement have been activated successfully!"})
    else:
        return JsonResponse({"status":"error","message": f"You are unauthorized to access this page!"})