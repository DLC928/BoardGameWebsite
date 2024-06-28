from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from boardgame.models import Group,Event


# Create your views here.

def home(request):
    group_list = Group.objects.all().order_by('name')
    event_list = Event.objects.all().order_by('title')
    context_dict = {
        'boldmessage': 'Join today!',
        'groups': group_list,
        'events': event_list
    }
    # Render the response and send it back!
    return render(request, 'boardgame/home.html', context=context_dict)

def group_profile(request, group_slug):
    # Retrieve the group object using the slug
    group = get_object_or_404(Group, slug=group_slug)
    # Pass the group object to the template
    context = {
        'group': group
    }
    return render(request, 'boardgame/group_profile.html', context)

def event_profile(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    context = {
        'event': event
    }
    return render(request, 'boardgame/event_profile.html', context)


def v1(request):
    return HttpResponse("View 1!")
