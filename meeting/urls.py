from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.meeting_home, name='meeting-home'),
    path('add', views.meeting_add, name='meeting-add'),
    path('add/agenda', views.agenda_add, name='agenda-add'),
    path('agenda/<int:pk>/add/response', views.response_add, name='response-add'),
    path('add/attendance', views.attendance, name='attendance'),
    path('view/attendance/<int:pk>', views.view_attendee, name='view-attendee'),
    path('<int:pk>/agenda', views.view_agenda, name='view-agenda'),
    path('view/<int:pk>', views.view_meeting, name='view-meeting'),
    path('close/<int:pk>/', views.close_meeting, name='close-meeting'),
    path('download/<int:pk>/', views.download_meeting, name='download-meeting'),
]