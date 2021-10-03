from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login', views.MyLoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('registration', views.signup_view, name='registration'),
    path('signout', views.signout, name='signout'),

    path('password_change', auth_views.PasswordChangeView.as_view(template_name='authentication/change_password.html'), name='change_password'),
    path('password_change/done', auth_views.PasswordChangeDoneView.as_view(template_name='authentication/change_password_done.html'), name='password_change_done'),


    path('password-reset', auth_views.PasswordResetView.as_view(template_name='authentication/password_reset_form.html'), name="forgotpass"),
    path('password-reset/done', auth_views.PasswordResetDoneView.as_view(template_name='authentication/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='authentication/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset/complete',auth_views.PasswordResetCompleteView.as_view(template_name='authentication/password_reset_complete.html'), name='password_reset_complete'),

]