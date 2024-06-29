from django.urls import path
from boardgame import views
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path("",views.home, name="home"),
    path('jsi18n', JavaScriptCatalog.as_view(), name='js-catlog'),
    path('group/<slug:group_slug>/', views.group_profile, name='group_profile'),
    path('event/<int:event_id>/', views.event_details, name='event_details'),
    path('create_group', views.create_group, name='create_group'),
    path('group/<slug:group_slug>/create_event/', views.create_event, name='create_event'),
    #path('event/<int:event_id>/nominate/', views.nominate_game, name='nominate_game'),
    
]
