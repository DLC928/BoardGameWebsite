from django.urls import path
from boardgame import views

urlpatterns = [
    path("",views.home, name="home"),
    path('group/<slug:group_slug>/', views.group_profile, name='group_profile'),
    path('event/<int:event_id>/', views.event_details, name='event_details'),
    path('create_group', views.create_group, name='create_group'),
    path('group/<slug:group_slug>/create_event/', views.create_event, name='create_event'),
    
]
