from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('member', views.view_all_members, name='view-member'),
    path('view/profile/<int:pk>/', views.view_user_profile, name='view-user-profile'),
    path('disable/member/<int:pk>/', views.disable_member, name='disable-member'),
    path('enable/member/<int:pk>/', views.enable_member, name='enable-member'),
    path('make/admin/<int:pk>/', views.make_admin, name='make-admin'),
    path('make/member/<int:pk>/', views.remove_admin, name='remove-admin'),
    path('subscription/add', views.add_subscription, name='add-subscription'), 
    path('add/announcement', views.add_announcement, name='add-announcement'), 
    path('view_announcement', views.view_announcement, name='view-announcement'), 
    path('unpublish/announcement/<int:pk>/', views.unpublish_announcement, name='unpublish-announcement'),
    path('publish/announcement/<int:pk>/', views.publish_announcement, name='publish-announcement'), 

    # path('view/meeting/<int:pk>/', views.view_meeting, name='view-meeting'),

]