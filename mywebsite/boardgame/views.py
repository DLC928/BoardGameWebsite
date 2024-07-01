from django.shortcuts import render, get_object_or_404, redirect
from boardgame.models import Group,Event,GroupMembers,EventAttendance,GameNomination
from .forms import GroupForm, EventForm, EventLocationForm, GameDetailForm


def home(request):
    group_list = Group.objects.all().order_by('name')
    event_list = Event.objects.all().order_by('title')
    context_dict = {
        'boldmessage': 'Join today!',
        'groups': group_list,
        'events': event_list
    }
    return render(request, 'boardgame/home.html', context=context_dict)

# ---------------------------GROUPS---------------------------
def group_profile(request, group_slug):
    # Retrieve the group object using the slug
    group = get_object_or_404(Group, slug=group_slug)
    is_admin = GroupMembers.objects.filter(user=request.user, group=group, is_admin=True).exists()

    # Fetch events associated with the group
    events = Event.objects.filter(group=group).order_by('title')


    # Pass the group object to the template
    context = {
        'group': group,
        'is_admin': is_admin,
        'events': events,
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

# ---------------------------EVENTS---------------------------
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
    nominations = event.nominations.all()
    is_attending = attendees.filter(id=request.user.id).exists() #check to see if current user is attending

    for nomination in nominations:
        print(nomination)  # Print each nomination object to inspect its attributes
        print(nomination.name)

    if request.method == 'POST': # used when a form has been submitted, meaning someone clicked button 
        if 'join' in request.POST: # based on button name in html page
            if not is_attending:
                EventAttendance.objects.create(user=request.user, event=event) #create() will create and save object in one step
        elif 'leave' in request.POST:
            if is_attending:
                EventAttendance.objects.filter(user=request.user, event=event).delete()
        return redirect('event_details', event_id=event_id)

    context = {
        'event': event,
        'attendees': attendees,
        'is_attending': is_attending,
        'nominations': nominations,
    }
    return render(request, 'boardgame/event_details.html', context)

def nominate_game(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = GameDetailForm(request.POST)
        if form.is_valid():
            game = form.save(commit=False)
            game.name = request.POST.get('name')
            game.description = request.POST.get('description')
            
            # Handle empty fields
            min_players = request.POST.get('min_players')
            max_players = request.POST.get('max_players')
            min_playtime = request.POST.get('min_playtime')
            max_playtime = request.POST.get('max_playtime')
            age = request.POST.get('age')
            weight = request.POST.get('weight')
            
            game.min_players = int(min_players) if min_players else None
            game.max_players = int(max_players) if max_players else None
            game.min_playtime = int(min_playtime) if min_playtime else None
            game.max_playtime = int(max_playtime) if max_playtime else None
            game.age = int(age) if age else None
            game.weight = float(weight) if weight else None
            
            game.save()
            
            GameNomination.objects.create(game=game, event=event, nominator=request.user)
            return redirect('event_details', event_id=event_id)
    else:
        form = GameDetailForm()
    
    return render(request, 'boardgame/nominate_game.html', {'form': form, 'event': event})