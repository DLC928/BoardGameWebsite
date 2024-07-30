from django.urls import path
from boardgame import views, api_views
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path("",views.home, name="home"),
    path('jsi18n', JavaScriptCatalog.as_view(), name='js-catlog'),
    path('api/search-games/', api_views.search_games, name='search_games'),
    path('api/game-details/', api_views.load_game_details, name='load_game_details'),
    path('group/<slug:group_slug>/', views.group_profile, name='group_profile'),
    path('event/<int:event_id>/', views.event_details, name='event_details'),
    path('create-group/', views.create_group, name='create_group'),
    path('group/<slug:group_slug>/create_event/', views.create_event, name='create_event'),
    path('event/<int:event_id>/nominate/', views.nominate_game, name='nominate_game'),
    path('event/<int:event_id>/game_details/<int:game_id>/', views.game_details, name='game_details'),
    path('profile/<int:id>', views.user_profile, name='user_profile'),
    path('profile-setup/', views.profile_setup, name='profile_setup'),
    path('profile-edit/', views.edit_profile, name='profile_edit'),
    path('groups/', views.groups, name='groups'),
    path('events/', views.events, name='events'),
    path('search/', views.search, name='search'),
    path('group-dashboard/<slug:group_slug>/', views.manage_group_dashboard, name='manage_group_dashboard'),
    path('group-dashboard/<slug:group_slug>/<str:section>/', views.manage_group_dashboard, name='manage_group_dashboard_with_section'),
    path('event-dashboard/event/<int:event_id>/', views.manage_event_dashboard, name='manage_event_dashboard'),
    path('event-dashboard/event/<int:event_id>/<str:section>/', views.manage_event_dashboard, name='manage_event_dashboard_with_section'),

]

 