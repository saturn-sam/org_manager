from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Count, Q, Sum, FilteredRelation
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.sites.shortcuts import get_current_site

from .forms import UserUpdateForm, ProfileUpdateForm, UserAdminCreationForm
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView

from authentication import models

from authentication.models import CustomUser

# Create your views here.


class MyLoginView(SuccessMessageMixin, LoginView):
    template_name = 'authentication/login.html'
    success_message = 'Successfully Logged In.'

def signup_view(request):
    if request.method  == 'POST':
        form = UserAdminCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.first_name = form.cleaned_data.get('first_name')
            user.profile.last_name = form.cleaned_data.get('last_name')
            user.profile.email = form.cleaned_data.get('email')
            user.is_active = False
            user.save()
            messages.success(request, 'Account has been created! Please wait until your account become verified by an admin. You will receive an email on approval.')
            return redirect('registration')
    else:
        form = UserAdminCreationForm()
    return render(request, 'authentication/registration.html', {'form': form})

@login_required
def signout(request):
    logout(request)
    return redirect('login')
