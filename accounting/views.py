from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import json

from django.db.models import CharField, Value as V, Sum, F, Q, FilteredRelation
from django.db.models.functions import Concat
from django.urls import reverse
from django.template.loader import render_to_string
import logging
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from io import BytesIO
from django.core.files import File
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.storage import FileSystemStorage
import xlwt

from weasyprint import HTML,CSS
import tempfile

from .forms import DepositForm, EarningForm, ExpenditureForm, DateRangeForm, AllEarningReportForm, AllExpTypeReportForm
from .models import Deposite, Subscriptionof, Earning, Expenditure, ReceiptID
from authentication.models import CustomUser
import os
# Create your views here.

logger = logging.getLogger(__name__)

@login_required
def accounts_dashboard(request):
    all_deposits = Deposite.objects.all().order_by('-insert_date')
    all_earnings = Earning.objects.all().order_by('-insert_date')
    all_expenditures = Expenditure.objects.all().order_by('-insert_date')
    month_wise_deposit = Subscriptionof.objects.annotate(deposite_user=FilteredRelation('deposite', condition=Q(deposite__member_name=request.user.id) & Q(deposite__approve_status=1))).values('subs_of', 'deposite_user__member_name__first_name').order_by('-id')
    due_counter = 0
    for i in month_wise_deposit:
        if not i['deposite_user__member_name__first_name']:
            due_counter+=1

    total_deposit_individual = Deposite.objects.filter(Q(member_name=request.user) & Q(approve_status=1)).aggregate(Sum('amount'))

    context = {
        'all_deposits' : all_deposits,
        'month_wise_deposit' : month_wise_deposit,
        'all_earnings' : all_earnings,
        'all_expenditures' : all_expenditures,
        'total_deposit_individual' : total_deposit_individual,
        'due_counter' : due_counter,

    }
    return render(request, 'accounting/accounts-dashboard.html', context)

@login_required
def submitdeposit(request):
    if request.method == 'POST':
        d_form = DepositForm(request.POST, request.FILES)
        if d_form.is_valid():
            get_user_deposit = Deposite.objects.filter(Q(member_name=d_form.cleaned_data['member_name']) & Q(sub_of=d_form.cleaned_data['sub_of']) & (Q(approve_status=0) | Q(approve_status=1)))
            if not get_user_deposit:
                deposit = d_form.save()
                deposit.refresh_from_db()
                deposit.insert_by = request.user
                deposit.save()
                logger.warning(f"User {request.user.get_full_name()} submitted a deposit request for user {d_form.cleaned_data['member_name']} for month {d_form.cleaned_data['sub_of']}")
                messages.success(request, 'Deposit information has been submitted. Please wait to be approved by an admin')
                return redirect('accounts-dashboard')
            else:
                messages.error(request, 'You have a subscription of this month which is not in Denied status. For detail contact admin.')
    else:
        d_form = DepositForm()

    context = {
        'd_form' : d_form
    }
    return render(request, 'accounting/deposit_submit.html', context)


def increment_invoice_number():
    last_invoice = ReceiptID.objects.all().order_by('id').last()
    if not last_invoice:
        invoice_no= 1
        ReceiptID.objects.create(invoice_no=invoice_no)
        return invoice_no
    else:
        invoice_no = last_invoice.invoice_no
        new_inv_no = invoice_no+1
        logging.warning(f"new invoice no. {new_inv_no} has been generated")
        ReceiptID.objects.create(invoice_no=new_inv_no)
        return new_inv_no

@login_required
def approve_deposit(request, pk):
    if request.user.is_staff:
        deposite = get_object_or_404(Deposite, id=pk)
        if deposite.approve_status == 0:
            import datetime
            if request.method == 'POST':
                member_instance = CustomUser.objects.get(id=deposite.member_name.id)
                subscription_month = Subscriptionof.objects.get(id=deposite.sub_of.id)
                member_deposit_id = "Member's Deposit"
                description_of_deposit = member_instance.get_full_name()+ ", " + subscription_month.subs_of
                Earning.objects.create(earning_source=member_deposit_id, description=description_of_deposit,amount=deposite.amount, insert_by=deposite.member_name, insert_date=timezone.now(), deposit_info=deposite, approve_status=1, approve_by=request.user, approve_date=timezone.now())
                logger.warning(f"earning_source {member_deposit_id}, description '{description_of_deposit}' approved by {request.user}")
                Deposite.objects.filter(id=pk).update(approve_status=1, approve_by=request.user, appove_date=timezone.now())
                logger.warning(f"Deposit id  {pk}, approved by {request.user}")


        ###########     PDF GENERATION          ################
                obj = Deposite.objects.get(id=pk)
                receipt_no=increment_invoice_number()
                obj.receipt_id=receipt_no
                obj.receipt_issue_date=timezone.now()
                obj.save()      
                current_site = get_current_site(request)
                if request.user.get_full_name():
                    approve_by = request.user.get_full_name()
                else:
                    approve_by = request.user.email
                context = {
                    'member': member_instance.get_full_name(),
                    'member_address1': member_instance.profile.pre_vill+", "+member_instance.profile.pre_po,
                    'member_address2': member_instance.profile.pre_ps+", "+member_instance.profile.pre_dist,
                    'subscription': subscription_month.subs_of, 
                    'amount': deposite.amount,
                    'receipt_no':receipt_no,
                    'phone':member_instance.profile.phone,
                    'issue_date':timezone.now(),
                    'approve_by':approve_by,
                    'logo':'{}{}{}{}'.format('http://',current_site,settings.STATIC_URL,'image/uttaran-logo.PNG')
                }

                html_string = render_to_string('mail_format/deposit_receipt_template.html', context)
                html = HTML(string=html_string)
                filename = "Receipt_"+subscription_month.subs_of+"_"+member_instance.email+".pdf"
                css_url = os.path.join(settings.BASE_DIR, 'static/vendor/bootstrap/css/bootstrap.css')
                filename_2 = os.path.join(settings.MEDIA_ROOT)+'/pdfs/'+filename
                result = html.write_pdf(target=filename_2, stylesheets=[CSS(css_url)])
                logger.warning(f"Receipt {filename} has been generated")
        ###########     PDF GENERATION          ################

        ###########     Mail Sending          ################

                message = render_to_string('mail_format/deposite-sent-mail-template.html', {
                            'member': member_instance,
                            'month': subscription_month,
                        }) 
                subject = 'Subscription confirmed for ' + subscription_month.subs_of
                send_to = member_instance.email
                email = EmailMessage(subject,message,settings.EMAIL_HOST_USER,[send_to])
                file_to_be_sent = os.path.join(settings.BASE_DIR, filename_2)
                email.attach_file(file_to_be_sent)
                email.content_subtype = "html" 
                email.send()
                logger.warning(f"Receipt {filename} has been mailed to {send_to}")
        ###########     Mail Sending          ################
     

                return JsonResponse({"status":"success","message": f"Deposit Information has been Approved! Confirmation receipt has been sent to user's email!"})
        elif deposite.approve_status == 1:
            return JsonResponse({"status":"error","message": f"Ooops! This deposit submission already has been approved!"})
        else:
            return JsonResponse({"status":"error","message": f"Ooops! This deposit submission already has been denied!"})        
    else:
        logger.warning("unauthorized access by {request.user}")
        return JsonResponse({"status":"error","message": f"You are unauthorized to access this page!"})

@login_required
def receipt_download(request, pk):
    deposite = get_object_or_404(Deposite, id=pk)
    member_instance = CustomUser.objects.get(id=deposite.member_name.id)
    subscription_month = Subscriptionof.objects.get(id=deposite.sub_of.id)

        ###########     PDF GENERATION          ################
    receipt_no=deposite.receipt_id   
    current_site = get_current_site(request) 
    if deposite.approve_by.get_full_name():
        approve_by = request.user.get_full_name()
    else:
        approve_by = request.user.email     
    context = {
        'member': member_instance.get_full_name(),
        'member_address1': member_instance.profile.pre_vill+", "+member_instance.profile.pre_po,
        'member_address2': member_instance.profile.pre_ps+", "+member_instance.profile.pre_dist,
        'subscription': subscription_month.subs_of, 
        'amount': deposite.amount,
        'receipt_no':receipt_no,
        'phone':member_instance.profile.phone,
        'issue_date':deposite.receipt_issue_date,
        'approve_by':approve_by,
        'logo':'{}{}{}{}'.format('http://',current_site,settings.STATIC_URL,'image/uttaran-logo.PNG')
    }

    html_string = render_to_string('mail_format/deposit_receipt_template.html', context)
    html = HTML(string=html_string)
    filename = "Receipt_"+subscription_month.subs_of+"_"+member_instance.get_full_name()+".pdf"
    css_url = os.path.join(settings.BASE_DIR, 'static/vendor/bootstrap/css/bootstrap.css')
    filename_2 = os.path.join(settings.MEDIA_ROOT)+'/pdfs/'+filename
    result = html.write_pdf(target=filename_2, stylesheets=[CSS(css_url)])    
    logger.warning(f"User {request.user} downloaded receipt {filename}")
    with open(filename_2, 'rb') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="member_subscription_wise_report.pdf"'
        return response
    redirect_to = 'accounts-dashboard'
    return HttpResponseRedirect (reverse(redirect_to)) 

        ###########     PDF GENERATION          ################



@login_required
def deny_deposit(request, pk):
    if request.user.is_staff:
        deposite = get_object_or_404(Deposite, id=pk)
        if deposite.approve_status == 0:
            import datetime
            if request.method == 'POST':
                Deposite.objects.filter(id=pk).update(approve_status=2, approve_by=request.user, appove_date=timezone.now())
                logger.warning(f" deposit {deposite.id} has been denied by {request.user}")
                return JsonResponse({"status":"success","message": f"Deposit Submission has been Denied Successfully"})
        elif deposite.approve_status == 1:
            return JsonResponse({"status":"error","message": f"Ooops! This deposit submission already has been approved!"})
        else:
            return JsonResponse({"status":"error","message": f"Ooops! This deposit submission already has been denied!"})
    else:
        return JsonResponse({"status":"error","message": f"You are unauthorized to access this page!"})


@login_required
def viewdeposit(request):
    all_deposits = Deposite.objects.filter(Q(member_name=request.user) | (Q(insert_by=request.user) & (Q(approve_status=0) | Q(approve_status=2)))).order_by('-insert_date')
    context = {
        'all_deposits' : all_deposits,
    }
    return render(request, 'accounting/diposit_view.html', context)

@login_required
def all_deposit(request):
    all_deposits = Deposite.objects.filter(approve_status = 1).order_by('-insert_date')
    total_deposit_all = Deposite.objects.filter(Q(approve_status=1)).aggregate(Sum('amount'))
    if not total_deposit_all['amount__sum']:
        total_deposit_all['amount__sum']=0
    context = {
        'all_deposits' : all_deposits,
        'total_deposit_all' : total_deposit_all,
    }
    return render(request, 'accounting/diposit_all.html', context)

@login_required
def other_earning(request):
    if request.method == 'POST':
        if 'show' in request.POST:        
            earning_source=request.POST.getlist('earning_source')
            print(earning_source)
            # if len(earning_source) < 1 :
            #     messages.warning(request,"Please select at least one field from list")
            # else:
            if 'all' in earning_source or not earning_source:
                earning = Earning.objects.filter(approve_status=1, delete_status=0).order_by('-id')
                earning_amount = Earning.objects.filter(approve_status=1, delete_status=0).aggregate(Sum('amount'))
                if not earning:
                    messages.warning(request,"No data found.")
                    context={
                        're_form':AllEarningReportForm(),
                    }
                    return render(request, 'accounting/diposit_all.html',context)
                else:
                    context={
                        'earnings':earning,
                        'earning_amount': earning_amount,
                        're_form':AllEarningReportForm(),
                    }
                    return render(request, 'accounting/diposit_all.html',context)
            else:
                earning = Earning.objects.filter(earning_source__in=earning_source, approve_status=1, delete_status=0).order_by('-id')
                earning_amount = Earning.objects.filter(earning_source__in=earning_source, approve_status=1, delete_status=0).aggregate(Sum('amount'))
                if not earning:
                    messages.warning(request,"No data found.")
                    context={
                        're_form':AllEarningReportForm(),
                    }
                    return render(request, 'accounting/diposit_all.html',context)
                else:
                    context={
                        'earnings':earning,
                        'earning_amount': earning_amount,
                        're_form':AllEarningReportForm(),
                    }
                    return render(request, 'accounting/diposit_all.html',context)                     
        elif 'download' in request.POST:
            earning_source=request.POST.getlist('earning_source')
            # if len(earning_source) < 1 :
            #     messages.warning(request,"Please select at least one field from list")
            # else:
            if 'all' in earning_source or not earning_source:
                earning = Earning.objects.filter(approve_status=1, delete_status=0).order_by('-id')
                earning_amount = Earning.objects.filter(approve_status=1, delete_status=0).aggregate(Sum('amount'))
                if not earning:
                    messages.warning(request,"No data found.")
                    context={
                        're_form':AllEarningReportForm(),
                    }
                    return render(request, 'accounting/diposit_all.html',context)
                else:
                    response = HttpResponse(content_type='application/ms-excel')
                    response['Content-Disposition'] = 'attachment; filename="Earning_Report.xls"'
                    wb = xlwt.Workbook(encoding='utf-8')
                    ws = wb.add_sheet("sheet1")
                    font_style = xlwt.XFStyle()
                    font_style.font.bold = True
                    columns = ['SL', 'Earning Source', 'Description', 'Info. Submitted by', 'Submission Date', 'Amount']
                    ws.write(0, 0, 'Uttaran', font_style)
                    ws.write(1, 0, 'Earning Reports', font_style)
                    row_num = 2
                    for col_num in range(len(columns)):
                        ws.write(row_num, col_num, columns[col_num], font_style)
                    font_style2 = xlwt.XFStyle()
                    sl=0
                    for my_row in earning:
                        row_num = row_num + 1
                        sl += 1
                        ws.write(row_num, 0, sl, font_style2)
                        ws.write(row_num, 1, my_row.earning_source, font_style2)
                        ws.write(row_num, 2, my_row.description, font_style2)
                        ws.write(row_num, 3, my_row.insert_by.first_name+" "+my_row.insert_by.last_name, font_style2)
                        ws.write(row_num, 4, timezone.make_naive(my_row.insert_date), font_style2)
                        ws.write(row_num, 5, my_row.amount, font_style2)
                    ws.write(row_num+1, 4, "Total", font_style)
                    ws.write(row_num+1, 5, earning_amount['amount__sum'], font_style)
                    wb.save(response)
                    return response
            else:
                earning = Earning.objects.filter(earning_source__in=earning_source, approve_status=1, delete_status=0).order_by('-id')
                earning_amount = Earning.objects.filter(earning_source__in=earning_source, approve_status=1, delete_status=0).aggregate(Sum('amount'))
                if not earning:
                    messages.warning(request,"No data found.")
                    context={
                        're_form':AllEarningReportForm(),
                    }
                    return render(request, 'accounting/diposit_all.html',context)
                else:
                    response = HttpResponse(content_type='application/ms-excel')
                    response['Content-Disposition'] = 'attachment; filename="Earning_Report.xls"'
                    wb = xlwt.Workbook(encoding='utf-8')
                    ws = wb.add_sheet("sheet1")
                    font_style = xlwt.XFStyle()
                    font_style.font.bold = True
                    columns = ['SL', 'Earning Source', 'Description', 'Info. Submitted by', 'Submission Date', 'Amount']
                    ws.write(0, 0, 'Uttaran', font_style)
                    ws.write(1, 0, 'Earning Reports', font_style)
                    row_num = 2
                    for col_num in range(len(columns)):
                        ws.write(row_num, col_num, columns[col_num], font_style)
                    font_style = xlwt.XFStyle()
                    sl=0
                    for my_row in earning:
                        row_num = row_num + 1
                        sl += 1
                        ws.write(row_num, 0, sl, font_style)
                        ws.write(row_num, 1, my_row.earning_source, font_style)
                        ws.write(row_num, 2, my_row.description, font_style)
                        ws.write(row_num, 3, my_row.insert_by.first_name+" "+my_row.insert_by.last_name, font_style)
                        ws.write(row_num, 4, timezone.make_naive(my_row.insert_date), font_style)
                        ws.write(row_num, 5, my_row.amount, font_style)
                    ws.write(row_num+1, 4, "Total", font_style)
                    ws.write(row_num+1, 5, earning_amount['amount__sum'], font_style)

                    wb.save(response)
                    return response                        
            return render(request, 'accounting/diposit_all.html',context)  

    else:   
        re_form = AllEarningReportForm() 
        context={
            're_form':re_form,
        }
        return render(request, 'accounting/diposit_all.html',context)

@login_required
def expenditure_report(request):
    if request.method == 'POST':
        if 'show' in request.POST:
            exp_type=request.POST.getlist('exp_type')
            # if len(exp_type) < 1 :
            #     messages.warning(request,"Please select at least one field from list")
            # else: 
            if 'all' in exp_type or not exp_type:
                exp = Expenditure.objects.filter(approve_status=1, delete_status=0).order_by('-id')
                exp_amount = Expenditure.objects.filter(approve_status=1, delete_status=0).aggregate(Sum('amount'))
                if not exp:
                    messages.warning(request,"No data found.")
                    context={
                        're_form':AllExpTypeReportForm(),
                    }
                    return render(request, 'accounting/exp_type_report.html',context) 
                else:
                    context={
                        'exps':exp,
                        'exp_amount': exp_amount,
                        're_form':AllExpTypeReportForm(),
                    }
                    return render(request, 'accounting/exp_type_report.html',context)
            else:
                exp = Expenditure.objects.filter(expenditure_type__in=exp_type, approve_status=1, delete_status=0).order_by('-id')
                exp_amount = Expenditure.objects.filter(expenditure_type__in=exp_type, approve_status=1, delete_status=0).aggregate(Sum('amount'))
                if not exp:
                    messages.warning(request,"No data found.")
                    context={
                        're_form':AllExpTypeReportForm(),
                    }
                    return render(request, 'accounting/diposit_all.html',context)
                else:
                    context={
                        'exps':exp,
                        'exp_amount': exp_amount,
                        're_form':AllExpTypeReportForm(),
                    }
                    return render(request, 'accounting/exp_type_report.html',context)                  
        elif 'download' in request.POST:
            exp_type=request.POST.getlist('exp_type')
            # if len(exp_type) < 1 :
            #     messages.warning(request,"Please select at least one field from list")
            # else: 
            if 'all' in exp_type or not exp_type:
                exp = Expenditure.objects.filter(approve_status=1, delete_status=0).order_by('-id')
                exp_amount = Expenditure.objects.filter(approve_status=1, delete_status=0).aggregate(Sum('amount'))
                if not exp:
                    messages.warning(request,"No data found.")
                    context={
                        're_form':AllExpTypeReportForm(),
                    }
                    return render(request, 'accounting/exp_type_report.html',context) 
                else:
                    response = HttpResponse(content_type='application/ms-excel')
                    response['Content-Disposition'] = 'attachment; filename="Earning_Report.xls"'
                    wb = xlwt.Workbook(encoding='utf-8')
                    ws = wb.add_sheet("sheet1")
                    font_style = xlwt.XFStyle()
                    font_style.font.bold = True
                    columns = ['SL', 'Expenditure Type', 'Expenditure Source', 'Description', 'Expenditure Date', 'Info. Submitted by','Submission Date','Approved By','Approval Date','Amount']
                    ws.write(0, 0, 'Uttaran', font_style)
                    ws.write(1, 0, 'Expenditure Reports', font_style)
                    row_num = 2
                    for col_num in range(len(columns)):
                        ws.write(row_num, col_num, columns[col_num], font_style)
                    font_style2 = xlwt.XFStyle()
                    sl=0
                    for my_row in exp:
                        row_num = row_num + 1
                        sl += 1
                        ws.write(row_num, 0, sl, font_style2)
                        ws.write(row_num, 1, my_row.expenditure_type, font_style2)
                        ws.write(row_num, 2, my_row.expenditure_source, font_style2)
                        ws.write(row_num, 3, my_row.description, font_style2)
                        ws.write(row_num, 4, my_row.expenditure_date, font_style2)
                        ws.write(row_num, 5, my_row.insert_by.first_name+" "+my_row.insert_by.last_name, font_style2)
                        ws.write(row_num, 6, timezone.make_naive(my_row.insert_date), font_style2)
                        ws.write(row_num, 7, my_row.approve_by.first_name+" "+my_row.approve_by.last_name, font_style2)
                        ws.write(row_num, 8, timezone.make_naive(my_row.approve_date), font_style2)
                        ws.write(row_num, 9, my_row.amount, font_style2)
                    ws.write(row_num+1, 8, "Total", font_style)
                    ws.write(row_num+1, 9, exp_amount['amount__sum'], font_style)
                    wb.save(response)
                    return response
            else:
                exp = Expenditure.objects.filter(expenditure_type__in=exp_type, approve_status=1, delete_status=0).order_by('-id')
                exp_amount = Expenditure.objects.filter(expenditure_type__in=exp_type, approve_status=1, delete_status=0).aggregate(Sum('amount'))
                if not exp:
                    messages.warning(request,"No data found.")
                    context={
                        're_form':AllExpTypeReportForm(),
                    }
                    return render(request, 'accounting/diposit_all.html',context)
                else:
                    response = HttpResponse(content_type='application/ms-excel')
                    response['Content-Disposition'] = 'attachment; filename="Earning_Report.xls"'
                    wb = xlwt.Workbook(encoding='utf-8')
                    ws = wb.add_sheet("sheet1")
                    font_style = xlwt.XFStyle()
                    font_style.font.bold = True
                    columns = ['SL', 'Expenditure Type', 'Expenditure Source', 'Description', 'Expenditure Date', 'Info. Submitted by','Submission Date','Approved By','Approval Date','Amount']
                    ws.write(0, 0, 'Uttaran', font_style)
                    ws.write(1, 0, 'Expenditure Reports', font_style)
                    row_num = 2
                    for col_num in range(len(columns)):
                        ws.write(row_num, col_num, columns[col_num], font_style)
                    font_style2 = xlwt.XFStyle()
                    sl=0
                    for my_row in exp:
                        row_num = row_num + 1
                        sl += 1
                        ws.write(row_num, 0, sl, font_style2)
                        ws.write(row_num, 1, my_row.expenditure_type, font_style2)
                        ws.write(row_num, 2, my_row.expenditure_source, font_style2)
                        ws.write(row_num, 3, my_row.description, font_style2)
                        ws.write(row_num, 4, my_row.expenditure_date, font_style2)
                        ws.write(row_num, 5, my_row.insert_by.first_name+" "+my_row.insert_by.last_name, font_style2)
                        ws.write(row_num, 6, timezone.make_naive(my_row.insert_date), font_style2)
                        ws.write(row_num, 7, my_row.approve_by.first_name+" "+my_row.approve_by.last_name, font_style2)
                        ws.write(row_num, 8, timezone.make_naive(my_row.approve_date), font_style2)
                        ws.write(row_num, 9, my_row.amount, font_style2)
                    ws.write(row_num+1, 8, "Total", font_style)
                    ws.write(row_num+1, 9, exp_amount['amount__sum'], font_style)
                    wb.save(response)
                    return response

    else:
        re_form = AllExpTypeReportForm() 
        context={
            're_form':re_form,
        }
        return render(request, 'accounting/exp_type_report.html',context)



@login_required
def submitearning(request):
    if request.method == 'POST':
        e_form = EarningForm(request.POST, request.FILES)
        if e_form.is_valid():
            earning = e_form.save()
            earning.refresh_from_db()
            earning.insert_date = timezone.now()
            earning.insert_by = request.user
            earning.save()
            messages.success(request, 'Earning information has been submitted. Please wait to be approbed by an admin')
            return redirect('accounts-dashboard')
    else:
        e_form = EarningForm()

    context = {
        'e_form' : e_form
    }
    return render(request, 'accounting/earning_submit.html', context)

@login_required
def approve_earning(request,pk):
    if request.user.is_staff:
        earning = get_object_or_404(Earning, id=pk)
        if earning.approve_status == 0:
            import datetime
            if request.method == 'POST':
                Earning.objects.filter(id=pk).update(approve_status=1, approve_by=request.user, approve_date=timezone.now())
                return JsonResponse({"status":"success","message": f"Earning Information has been Approved Successfully!"})
        elif earning.approve_status == 1:
            return JsonResponse({"status":"error","message": f"Ooops! This earning submission already has been approved!"})
        else:
            return JsonResponse({"status":"error","message": f"Ooops! This earning submission already has been denied!"})            
    else:
        return JsonResponse({"status":"error","message": f"You are unauthorized to access this page!"})  


@login_required
def deny_earning(request,pk):
    if request.user.is_staff:
        earning = get_object_or_404(Earning, id=pk)
        if earning.approve_status == 0:
            import datetime
            if request.method == 'POST':
                
                Earning.objects.filter(id=pk).update(approve_status=2, approve_by=request.user, approve_date=timezone.now())
                
                return JsonResponse({"status":"success","message": f"Earning Information has been Denied Successfully!"})
        elif earning.approve_status == 1:
            return JsonResponse({"status":"error","message": f"Ooops! This earning submission already has been approved!"})
        else:
            return JsonResponse({"status":"error","message": f"Ooops! This earning submission already has been denied!"}) 
    else:
        return JsonResponse({"status":"error","message": f"You are unauthorized to access this page!"}) 

@login_required
def deny_expenditure(request,pk):
    if request.user.is_staff:   
        expenditure = get_object_or_404(Expenditure, id=pk)
        if expenditure.approve_status == 0:
            import datetime
            if request.method == 'POST':
                Expenditure.objects.filter(id=pk).update(approve_status=2, approve_by=request.user, approve_date=timezone.now())
                return JsonResponse({"status":"success","message": f"Expenditure Information has been Denied Successfully!"})
        elif expenditure.approve_status == 1:
            return JsonResponse({"status":"error","message": f"Ooops! This expenditure submission already has been approved!"})
        else:
            return JsonResponse({"status":"error","message": f"Ooops! This expenditure submission already has been denied!"}) 
    else:
        return JsonResponse({"status":"error","message": f"You are unauthorized to access this page!"}) 


@login_required
def approve_expenditure(request,pk):
    if request.user.is_staff:    
        expenditure = get_object_or_404(Expenditure, id=pk)
        if expenditure.approve_status == 0:
            import datetime
            
            if request.method == 'POST':
                Expenditure.objects.filter(id=pk).update(approve_status=1, approve_by=request.user, approve_date=timezone.now())
                return JsonResponse({"status":"success","message": f"Expenditure Information has been Approved Successfully!"})
        elif expenditure.approve_status == 1:
            return JsonResponse({"status":"error","message": f"Ooops! This expenditure submission already has been approved!"})
        else:
            return JsonResponse({"status":"error","message": f"Ooops! This expenditure submission already has been denied!"}) 
    else:
        return JsonResponse({"status":"error","message": f"You are unauthorized to access this page!"}) 

@login_required
def viewearning(request):
    all_earnings = Earning.objects.filter(Q(insert_by=request.user)).order_by('-insert_date')
    context = {
        'all_earnings' : all_earnings,
    }
    return render(request, 'accounting/earning_view.html', context)

@login_required
def submitexpenditure(request):
    if request.method == 'POST':
        ex_form = ExpenditureForm(request.POST, request.FILES)
        if ex_form.is_valid():
            expenditure = ex_form.save()
            expenditure.refresh_from_db()
            expenditure.insert_by = request.user
            expenditure.save()
            messages.success(request, 'Expenditure information has been submitted successfully. Please wait to be approbed by an admin')
            return redirect('accounts-dashboard')
    else:
        ex_form = ExpenditureForm()

    context = {
        'ex_form' : ex_form
    }
    return render(request, 'accounting/expenditure_submit.html', context)

@login_required
def viewexpenditure(request):
    all_expenditures = Expenditure.objects.filter(Q(insert_by=request.user)).order_by('-insert_date')
    context = {
        'all_expenditures' : all_expenditures,
    }
    return render(request, 'accounting/expenditure_view.html', context)

@login_required
def deposit_report(request):
    import datetime
    deposits=[]
    sum_amount=0
    if request.method == 'POST':
        if 'show' in request.POST:
            form_dr = DateRangeForm(request.POST)
            if form_dr.is_valid():
                start_date=str(form_dr.cleaned_data['start_date']).split()[0]+' 00:00:00'
                end_date=str(form_dr.cleaned_data['end_date']).split()[0]+' 23:59:59'
                deposits = Deposite.objects.filter(insert_date__range=[start_date,end_date], approve_status = 1)
                sum_amount = Deposite.objects.filter(insert_date__range=[start_date,end_date],approve_status = 1).aggregate(Sum('amount'))
                if not deposits:
                    messages.warning(request,"No data found from "+str(start_date)+" to "+str(end_date)+".")
        elif 'download' in request.POST:
            form_dr = DateRangeForm(request.POST)
            if form_dr.is_valid():
                start_date=str(form_dr.cleaned_data['start_date']).split()[0]+' 00:00:00'
                end_date=str(form_dr.cleaned_data['end_date']).split()[0]+' 23:59:59'
                deposits = Deposite.objects.filter(insert_date__range=[start_date,end_date], approve_status = 1)
                sum_amount = Deposite.objects.filter(insert_date__range=[start_date,end_date],approve_status = 1).aggregate(Sum('amount'))

                if not deposits:
                    messages.warning(request,"No data found from "+str(start_date)+" to "+str(end_date)+".")  
                else:
                    response = HttpResponse(content_type='application/ms-excel')
                    response['Content-Disposition'] = 'attachment; filename="Deposit_Report_Date_Range_Wise.xls"'
                    wb = xlwt.Workbook(encoding='utf-8')
                    ws = wb.add_sheet("sheet1")
                    font_style = xlwt.XFStyle()
                    font_style.font.bold = True
                    columns = ['SL', 'Member Name', 'Subscription Month', 'Info. Submitted by', 'Submission Date', 'Approved By','Approval Date','Amount']
                    ws.write(0, 0, 'Uttaran', font_style)
                    ws.write(1, 0, 'Deposit Reports(Date Range)', font_style)
                    row_num = 2
                    for col_num in range(len(columns)):
                        ws.write(row_num, col_num, columns[col_num], font_style)
                    font_style2 = xlwt.XFStyle()
                    sl=0
                    for my_row in deposits:
                        row_num = row_num + 1
                        sl += 1
                        ws.write(row_num, 0, sl, font_style2)
                        ws.write(row_num, 1, my_row.member_name.first_name+" "+my_row.member_name.last_name, font_style2)
                        ws.write(row_num, 2, my_row.sub_of.subs_of, font_style2)
                        ws.write(row_num, 3, my_row.insert_by.first_name+" "+my_row.insert_by.last_name, font_style2)
                        ws.write(row_num, 4, timezone.make_naive(my_row.insert_date), font_style2)
                        ws.write(row_num, 5, my_row.approve_by.first_name+" "+my_row.approve_by.last_name, font_style2)
                        ws.write(row_num, 6, timezone.make_naive(my_row.appove_date), font_style2)
                        ws.write(row_num, 7, my_row.amount, font_style2)
                    ws.write(row_num+1, 6, "Total", font_style)
                    ws.write(row_num+1, 7, sum_amount['amount__sum'], font_style)
                    wb.save(response)
                    return response
    else:
        form_dr = DateRangeForm()
        deposits = []
    context = {
            "form_dr":form_dr,
            "deposits":deposits,
            'sum_amount':sum_amount,
        }
    return render(request, 'accounting/deposit_report_date_range.html', context)

@login_required
def due_report(request):
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

    if len(new_dict) < 1:
        messages.warning(request,"No data found.")  
    else:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="member_due_list.xls"'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet("sheet1")
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = ['SL', 'Member Name', 'Due']
        ws.write(0, 0, 'Uttaran', font_style)
        ws.write(1, 0, 'Members Due List', font_style)
        row_num = 2
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
        font_style2 = xlwt.XFStyle()
        sl=0
        for key in new_dict.keys():
            row_num = row_num + 1
            sl += 1
            col = 1
            ws.write(row_num, 0, sl, font_style2)
            ws.write(row_num, 1, key, font_style2)
            for i in new_dict.get(key):
                col += 1
                ws.write(row_num, col, i, font_style2)
            
        wb.save(response)
        return response

@login_required
def deposit_report_user_subs_of(request):
    members=CustomUser.objects.all()
    subs=Subscriptionof.objects.all()
    member_list=[]
    deposits = 0
    sum_amount = 0
    if request.method == 'POST':
        if 'show' in request.POST:        
            member_list=request.POST.getlist('member')
            subs_list=request.POST.getlist('subs')
            member_id_list = ""
            subs_id_list = ""
            if len(member_list) < 1 or len(subs_list) < 1:
                messages.warning(request,"Please select at least one field from both list")
            else:
                member_id_list = " ("
                subs_id_list = " ("
                if 'all' in member_list:
                    member_id_list = member_id_list+"member_name_id LIKE "+"'%%'"
                else:
                    for i in range(0,len(member_list),1) :
                        if member_list[i] == member_list[0]:
                            member_id_list = member_id_list+"member_name_id = "+member_list[i]
                        else:
                            member_id_list = member_id_list+" OR member_name_id = "+member_list[i]
                if 'all' in subs_list:
                    subs_id_list = subs_id_list+"sub_of_id LIKE "+"'%%'"
                    
                else:
                    for i in range(0,len(subs_list),1) :
                        if subs_list[i] == subs_list[0]:
                            subs_id_list = subs_id_list+"sub_of_id = "+subs_list[i]
                        else:
                            subs_id_list = subs_id_list+" OR sub_of_id = "+subs_list[i] 
                member_id_list = member_id_list+") "  
                subs_id_list = subs_id_list+") "     
                deposits = Deposite.objects.raw('select * from accounting_deposite where '+member_id_list+' and '+subs_id_list+' and approve_status=1' )
                sum_amount = Deposite.objects.raw('select id,  sum(amount) as sum_a from accounting_deposite where '+member_id_list+' and '+subs_id_list+' and approve_status=1')
                if not deposits:
                    messages.warning(request,"No data found.")                  
        elif 'download' in request.POST:
            member_list=request.POST.getlist('member')
            subs_list=request.POST.getlist('subs')
            member_id_list = ""
            subs_id_list = ""
            if len(member_list) < 1 or len(subs_list) < 1:
                messages.warning(request,"Please select at least one field from both list")
            else:
                member_id_list = " ("
                subs_id_list = " ("
                if 'all' in member_list:
                    member_id_list = member_id_list+"member_name_id LIKE "+"'%%'"
                else:
                    for i in range(0,len(member_list),1) :
                        if member_list[i] == member_list[0]:
                            member_id_list = member_id_list+"member_name_id = "+member_list[i]
                        else:
                            member_id_list = member_id_list+" OR member_name_id = "+member_list[i]
                if 'all' in subs_list:
                    subs_id_list = subs_id_list+"sub_of_id LIKE "+"'%%'"
                    
                else:
                    for i in range(0,len(subs_list),1) :
                        if subs_list[i] == subs_list[0]:
                            subs_id_list = subs_id_list+"sub_of_id = "+subs_list[i]
                        else:
                            subs_id_list = subs_id_list+" OR sub_of_id = "+subs_list[i] 
                member_id_list = member_id_list+") "  
                subs_id_list = subs_id_list+") "    
  
                deposits = Deposite.objects.raw('select * from accounting_deposite where '+member_id_list+' and '+subs_id_list+' and approve_status=1' )
                sum_amount = Deposite.objects.raw('select id,  sum(amount) as sum_a from accounting_deposite where '+member_id_list+' and '+subs_id_list+' and approve_status=1')
                if not deposits:
                    messages.warning(request,"No data found!")  
                else:
                    response = HttpResponse(content_type='application/ms-excel')
                    response['Content-Disposition'] = 'attachment; filename="Deposit_Report_Member_Wise.xls"'
                    wb = xlwt.Workbook(encoding='utf-8')
                    ws = wb.add_sheet("sheet1")
                    font_style = xlwt.XFStyle()
                    font_style.font.bold = True
                    columns = ['SL', 'Member Name', 'Subscription Month', 'Info. Submitted by', 'Submission Date', 'Approved By','Approval Date','Amount']
                    ws.write(0, 0, 'Uttaran', font_style)
                    ws.write(1, 0, 'Deposit Reports(Member and Subscription)', font_style)
                    row_num = 2
                    for col_num in range(len(columns)):
                        ws.write(row_num, col_num, columns[col_num], font_style)
                    font_style2 = xlwt.XFStyle()
                    sl=0
                    for my_row in deposits:
                        row_num = row_num + 1
                        sl += 1
                        ws.write(row_num, 0, sl, font_style2)
                        ws.write(row_num, 1, my_row.member_name.first_name+" "+my_row.member_name.last_name, font_style2)
                        ws.write(row_num, 2, my_row.sub_of.subs_of, font_style2)
                        ws.write(row_num, 3, my_row.insert_by.first_name+" "+my_row.insert_by.last_name, font_style2)
                        ws.write(row_num, 4, timezone.make_naive(my_row.insert_date), font_style2)
                        ws.write(row_num, 5, my_row.approve_by.first_name+" "+my_row.approve_by.last_name, font_style2)
                        ws.write(row_num, 6, timezone.make_naive(my_row.appove_date), font_style2)
                        ws.write(row_num, 7, my_row.amount, font_style2)
                    ws.write(row_num+1, 6, "Total", font_style)
                    for sum in sum_amount:
                        ws.write(row_num+1, 7, sum.sum_a, font_style)
                    
                    wb.save(response)
                    return response
    context={
        'members':members,
        'subs':subs,
        'deposits':deposits,
        'sum_amount':sum_amount,
    }
    return render(request, 'accounting/deposit_report_member_subs_of.html',context)
