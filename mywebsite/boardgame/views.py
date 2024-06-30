from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from boardgame.models import Group,Event,GroupMembers,EventAttendance
from .forms import GroupForm, EventForm, EventLocationForm


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
    is_admin = GroupMembers.objects.filter(user=request.user, group=group, is_admin=True).exists()
    # Pass the group object to the template
    context = {
        'group': group,
        'is_admin': is_admin
    }
    return render(request, 'boardgame/group_profile.html', context)


def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.save()
            
            # Add the current user as a member of the group and mark them as admin
            GroupMembers.objects.create(user=request.user, group=group, is_admin=True)
            return redirect('group_profile', group_slug=group.slug)
    else:
        form = GroupForm()
    return render(request, 'boardgame/create_group.html', {'form': form})

def create_event(request, group_slug):
    group = get_object_or_404(Group, slug=group_slug)
    if request.method == 'POST':
        event_form = EventForm(request.POST)
        location_form = EventLocationForm(request.POST)
        
        if event_form.is_valid() and location_form.is_valid():
            location = location_form.save()
            event = event_form.save(commit=False)
            event.group = group  # Associate the event with the group
            event.location = location  # Associate the event with the location
            event.save()
            return redirect('group_profile', group_slug=group_slug)
    else:
        event_form = EventForm()
        location_form = EventLocationForm()

    context = {
        'form': event_form,
        'location_form': location_form,
        'group': group,
    }
    return render(request, 'boardgame/create_event.html', context)

def event_details(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    attendees = event.attendees.all()
    is_attending = attendees.filter(id=request.user.id).exists() #check to see if current user is attending

    if request.method == 'POST': # used when a form has been submitted, meaning someone clicked button 
        if 'join' in request.POST: # based on button name in html page
            if not is_attending:
                EventAttendance.objects.create(user=request.user, event=event) #create() will create and save object in one step
        elif 'leave' in request.POST:
            if is_attending:
                EventAttendance.objects.filter(user=request.user, event=event).delete()
        elif 'nominate_game' in request.POST:
            if is_attending:
                pass # will bring to game nominate form later
        return redirect('event_details', event_id=event_id)

    context = {
        'event': event,
        'attendees': attendees,
        'is_attending': is_attending,
    }
    return render(request, 'boardgame/event_details.html', context)


