from django.urls import path
from boardgame import views

urlpatterns = [
    path("",views.home, name="home"),
    path('group/<slug:group_slug>/', views.group_profile, name='group_profile'),
    path('event/<int:event_id>/', views.event_profile, name='event_profile'),
]
