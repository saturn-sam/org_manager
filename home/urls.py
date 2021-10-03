from django.contrib import admin
from django.urls import path, include
#from .views import PostListView
from .views import index, profile, profileedit

urlpatterns = [
    path('', index, name='home'),
    path('profile', profile, name='profile'),
    path('edit-profile', profileedit, name='profile-edit'),
]