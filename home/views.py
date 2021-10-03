from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.
from django.db.models import Count, Q, Sum, FilteredRelation
from django.utils import timezone
from authentication.models import Profile, CustomUser
from authentication.forms import UserUpdateForm, ProfileUpdateForm
from accounting.models import Deposite, Earning, Expenditure, Subscriptionof
from management.models import Announcement
from meeting.models import Meeting


@login_required
def index(request):
    pending_user_approval = Profile.objects.filter(disable_status=0, user__is_active=0 ).count()
    if not pending_user_approval:
        pending_user_approval = 0
    pending_deposit = Deposite.objects.filter(approve_status=0).count()
    if not pending_deposit:
        pending_deposit = 0
    pending_earning = Earning.objects.filter(approve_status=0).count()
    if not pending_earning:
        pending_earning = 0
    pending_expenditure = Expenditure.objects.filter(approve_status=0).count()
    if not pending_expenditure:
        pending_expenditure = 0
    open_meeting = Meeting.objects.filter(final_approval=0).count()
    if not open_meeting:
        open_meeting = 0

    total_user = CustomUser.objects.filter(is_active=1).count()
    total_deposit_all = Deposite.objects.filter(Q(approve_status=1)).aggregate(Sum('amount'))
    if not total_deposit_all['amount__sum']:
        total_deposit_all['amount__sum']=0
    
    total_earning_all = Earning.objects.filter(Q(approve_status=1)).aggregate(Sum('amount'))
    if not total_earning_all['amount__sum']:   
        total_earning_all['amount__sum']=0 

    total_earning_other = Earning.objects.filter(~Q(earning_source = "Member's Deposit") & Q(approve_status = 1)).aggregate(Sum('amount'))
    if not total_earning_other['amount__sum']:
        total_earning_other['amount__sum']=0

    total_expenditure = Expenditure.objects.filter(Q(approve_status = 1)).aggregate(Sum('amount'))
    if not total_expenditure['amount__sum']:
        total_expenditure['amount__sum']=0

    total_expenditure_other_than_savings = Expenditure.objects.filter(Q(approve_status = 1) & ~Q(expenditure_type = "Savings")).aggregate(Sum('amount'))
    if not total_expenditure_other_than_savings['amount__sum']:
        total_expenditure_other_than_savings['amount__sum']=0

    total_savings = Expenditure.objects.filter(Q(approve_status = 1) & Q(expenditure_type = "Savings")).aggregate(Sum('amount'))
    if not total_savings['amount__sum']:
        total_savings['amount__sum']=0

    liquid_cash_on_hand = total_earning_all['amount__sum'] - total_expenditure['amount__sum']

    ###########For all Members Due Count##########

    all_users = CustomUser.objects.all()
    month_wise_deposit_all = Subscriptionof.objects.annotate(deposite_user=FilteredRelation('deposite', condition=Q(deposite__approve_status=1))).values('subs_of', 'deposite_user__member_name__first_name', 'deposite_user__member_name__id').order_by('-id')
    all_subs_of = Subscriptionof.objects.all()
    new_dict = {}
    for i in all_users:
        new_list = []
        user_due  = []

        for j in all_subs_of:
            
            for k in month_wise_deposit_all:
                if i.id == k['deposite_user__member_name__id'] :
                    new_list.append(k["subs_of"])
            counter = 0
            for m in new_list:
                if m == str(j.subs_of):
                    counter += 1
            if counter == 0:
                user_due.append(j.subs_of)
        new_dict[i.get_full_name()] = user_due
    ###########For all Members Due Count########## 

    announcements = Announcement.objects.filter(announce_dismiss_date__gte = timezone.now(), unpublish_status = '0')
    member_deposit_labels = []
    member_deposit_data = []
    queryset = Deposite.objects.values('member_name__first_name','member_name__last_name').annotate(total_deposit=Sum('amount')).filter(approve_status = 1).order_by('-total_deposit')
    for member in queryset:
        member_name = member['member_name__first_name'] + " " + member['member_name__last_name']
        member_deposit_labels.append(member_name)
        member_deposit_data.append(member['total_deposit']) 

    context={
        'user_count' : total_user,
        'total_deposit_all' : total_deposit_all,
        'total_earning_other' : total_earning_other,
        'total_expenditure' : total_expenditure,
        'total_expenditure_other_than_savings' : total_expenditure_other_than_savings,
        'total_savings' : total_savings,
        'total_earning_all' : total_earning_all,
        'liquid_cash_on_hand' : liquid_cash_on_hand,
        'member_deposit_labels' : member_deposit_labels,
        'member_deposit_data' : member_deposit_data,
        'new_dict' : new_dict,
        'announcements':announcements,
        'pending_user_approval': pending_user_approval,
        'pending_deposit': pending_deposit,
        'pending_earning': pending_earning,
        'pending_expenditure': pending_expenditure,
        'open_meeting': open_meeting
    }
    return render(request, 'index.html', context)


@login_required
def profile(request):
    from datetime import date
    age = int((date.today() - request.user.profile.dob).days/365.2425)
    context = {
        'age' : age
    }
    return render(request, 'home/profile.html', context)

@login_required
def profileedit(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)  

    context = {
        'u_form' : u_form,
        'p_form' : p_form
    }
    return render(request, 'home/profile-edit.html', context)