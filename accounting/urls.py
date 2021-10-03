from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('deposit/submit', views.submitdeposit, name='deposit-submit'),
    path('deposit/view', views.viewdeposit, name='deposit-view'),
    path('dashboard', views.accounts_dashboard, name='accounts-dashboard'),
    path('deposit/deny/<int:pk>', views.deny_deposit, name='deny-deposit'),
    path('deposit/approve/<int:pk>', views.approve_deposit, name='approve-deposit'),
    path('earning/submit', views.submitearning, name='earning-submit'),
    path('earning/view', views.viewearning, name='earning-view'),
    path('earning/approve/<int:pk>', views.approve_earning, name='approve-earning'),
    path('earning/deny/<int:pk>', views.deny_earning, name='deny-earning'),
    path('expenditure/submit', views.submitexpenditure, name='expenditure-submit'),
    path('expenditure/view', views.viewexpenditure, name='expenditure-view'),
    path('expenditure/approve/<int:pk>', views.approve_expenditure, name='approve-expenditure'),
    path('expenditure/deny/<int:pk>', views.deny_expenditure, name='deny-expenditure'),
    path('deposit/report', views.deposit_report, name='deposit-report'),
    path('deposit/report2', views.deposit_report_user_subs_of, name='deposit-report2'),
    path('receipt/download/<int:pk>', views.receipt_download, name='receipt-download'),

    # path('deposit/all', views.all_deposit, name='deposit-all'),
    path('earning', views.other_earning, name='other-earning'),
    path('expenditure', views.expenditure_report, name='expenditure-report'),
    path('due_report', views.due_report, name='due-report'),

]