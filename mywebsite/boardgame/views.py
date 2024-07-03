from django.shortcuts import render, get_object_or_404, redirect
from boardgame.models import GameSignup, Group,Event,GroupMembers,EventAttendance,GameNomination,Game
from .forms import GroupForm, EventForm, EventLocationForm, GameDetailForm


def home(request):
    # Fetch all groups and events
    group_list = Group.objects.all().order_by('name')
    event_list = Event.objects.all().order_by('title')
    
    # Initialize user-related variables
    user_groups = None
    user_events = None
    user = request.user
    
    # Check if the user is authenticated
    if user.is_authenticated:
        # Fetch user-specific groups and events
        user_groups = GroupMembers.objects.filter(user=user).select_related('group')
        user_events = EventAttendance.objects.filter(user=user).select_related('event')

    context = {
        'groups': group_list,
        'events': event_list,
        'user_groups': user_groups,
        'user_events': user_events,
    }

    return render(request, 'boardgame/home.html', context=context)


# ---------------------------GROUPS---------------------------

def groups(request):
    group_list = Group.objects.all().order_by('name')
    user_groups = None
    user = request.user

    if user.is_authenticated:
        user_groups = GroupMembers.objects.filter(user=user).select_related('group')

    context = {
        'groups': group_list,
        'user_groups': user_groups,
    }
    return render(request, 'boardgame/groups.html', context=context)


def group_profile(request, group_slug):
    # Retrieve the group object using the slug
    group = get_object_or_404(Group, slug=group_slug)
    members = group.members.all()

    # Determine if the user is authenticated and whether they are a member or admin
    is_member = False
    is_admin = False
    if request.user.is_authenticated:
        is_member = members.filter(id=request.user.id).exists()
        is_admin = GroupMembers.objects.filter(user=request.user, group=group, is_admin=True).exists()

    # Fetch events associated with the group
    events = Event.objects.filter(group=group).order_by('title')

    # Process join/leave group actions
    if request.method == 'POST' and request.user.is_authenticated:
        if 'join' in request.POST:
            if not is_member:
                GroupMembers.objects.create(user=request.user, group=group, is_admin=False)
        elif 'leave' in request.POST:
            if is_member:
                GroupMembers.objects.filter(user=request.user, group=group).delete()
        return redirect('group_profile', group_slug=group.slug)

    # Pass the group object and related data to the template
    context = {
        'group': group,
        'is_admin': is_admin,
        'events': events,
        'members': members,
        'is_member': is_member,
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
def events(request):
    event_list = Event.objects.all().order_by('title')
    user_events = None
    user = request.user
    
    # Check if the user is authenticated
    if user.is_authenticated:
        user_events = EventAttendance.objects.filter(user=user).select_related('event')

    context = {
        'events': event_list,
        'user_events': user_events,
    }
    return render(request, 'boardgame/events.html', context=context)

 

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
    nominations = event.gamenomination_set.all()
    
    is_attending = False
    if request.user.is_authenticated:
        is_attending = attendees.filter(id=request.user.id).exists()

    nominations_with_slots = []
    for nomination in nominations:
        signed_up_count = GameSignup.objects.filter(nomination=nomination).count()
        remaining_slots = nomination.game.max_players - signed_up_count
        is_signed_up = False
        if request.user.is_authenticated:
            is_signed_up = GameSignup.objects.filter(nomination=nomination, user=request.user).exists()
        nominations_with_slots.append({
            'nomination': nomination,
            'remaining_slots': remaining_slots,
            'is_signed_up': is_signed_up
        })

    if request.method == 'POST':
        if 'join' in request.POST:
            if not is_attending:
                EventAttendance.objects.create(user=request.user, event=event)
        elif 'leave' in request.POST:
            if is_attending:
                EventAttendance.objects.filter(user=request.user, event=event).delete()
                
                # Remove game signups and nominations if the user leaves the event
                for nomination in nominations:
                    # Remove user from game signups
                    GameSignup.objects.filter(user=request.user, nomination=nomination).delete()
                    
                    # Check if the user is the nominator and remove nomination
                    if nomination.nominator == request.user:
                        # Remove all signups for this nomination
                        GameSignup.objects.filter(nomination=nomination).delete()
                        # Remove the nomination itself
                        nomination.delete()
    
        elif 'sign_up' in request.POST:
            nomination_id = request.POST.get('nomination_id')
            nomination = get_object_or_404(GameNomination, id=nomination_id)
            if is_attending and not GameSignup.objects.filter(nomination=nomination, user=request.user).exists():
                GameSignup.objects.create(nomination=nomination, user=request.user)
        
        elif 'leave_game' in request.POST:
            nomination_id = request.POST.get('nomination_id')
            nomination = get_object_or_404(GameNomination, id=nomination_id)
            if GameSignup.objects.filter(nomination=nomination, user=request.user).exists():
                if nomination.nominator == request.user:
                    GameSignup.objects.filter(nomination=nomination).delete()
                    nomination.delete()
                    return redirect('event_details', event_id=event_id)
                else:
                    GameSignup.objects.filter(nomination=nomination, user=request.user).delete()
             
        elif 'remove_nomination' in request.POST:
            nomination_id = request.POST.get('nomination_id')
            nomination = get_object_or_404(GameNomination, id=nomination_id)
            if nomination.nominator == request.user:
                # Remove all signups for this nomination
                GameSignup.objects.filter(nomination=nomination).delete()
                # Remove the nomination itself
                nomination.delete()
        
        return redirect('event_details', event_id=event_id)

    context = {
        'event': event,
        'is_attending': is_attending,
        'nominations': nominations,
        'attendees': attendees,
        'nominations_with_slots': nominations_with_slots,
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
            
             # Create GameNomination and GameSignup
            nomination = GameNomination.objects.create(game=game, event=event, nominator=request.user)
            GameSignup.objects.create(nomination=nomination, user=request.user)


            return redirect('event_details', event_id=event_id)
    else:
        form = GameDetailForm()
    
    return render(request, 'boardgame/nominate_game.html', {'form': form, 'event': event})

def game_details(request, event_id, game_id):
    event = get_object_or_404(Event, id=event_id)
    game = get_object_or_404(Game, id=game_id)
    game_nomination = get_object_or_404(GameNomination, event=event, game=game)
    
    is_attending = False
    is_signed_up = False
    if request.user.is_authenticated:
        is_attending = event.attendees.filter(id=request.user.id).exists()
        is_signed_up = GameSignup.objects.filter(nomination=game_nomination, user=request.user).exists()

    # Calculate remaining sign-up slots
    signed_up_count = GameSignup.objects.filter(nomination=game_nomination).count()
    remaining_slots = game.max_players - signed_up_count

    # Retrieve the list of players signed up for this game
    game_signup_set = GameSignup.objects.filter(nomination=game_nomination)

    if request.method == 'POST':
        if 'sign_up' in request.POST:
            if not is_signed_up:
                # Create a new GameSignup entry for the current user
                GameSignup.objects.create(nomination=game_nomination, user=request.user)
        elif 'leave' in request.POST:
            if is_signed_up:
                # Check if the user is the nominator
                if game_nomination.nominator == request.user:
                    # Remove all signups for this nomination
                    GameSignup.objects.filter(nomination=game_nomination).delete()
                    # Remove the nomination itself
                    game_nomination.delete()
                    # Redirect to event details if the nominator leaves
                    return redirect('event_details', event_id=event_id)
                else:
                    # Remove the GameSignup entry for the current user
                    GameSignup.objects.filter(nomination=game_nomination, user=request.user).delete()

        # Redirect back to the same page after processing the form
        return redirect('game_details', event_id=event_id, game_id=game_id)


    context = {
        'event': event,
        'game': game,
        'is_attending': is_attending,
        'is_signed_up': is_signed_up,
        'remaining_slots': remaining_slots,
        'game_signup_set': game_signup_set,  # Include game_signup_set in the context
    }
    return render(request, 'boardgame/game_details.html', context)

# ---------------------------USER PROFILES---------------------------

def user_profile(request):
    user = request.user
    # Fetch all groups where the user is a member
    user_groups = GroupMembers.objects.filter(user=user).select_related('group')
    
    # Fetch all events where the user is attending
    user_events = EventAttendance.objects.filter(user=user).select_related('event')
    
    context = {
        'user_groups': user_groups,
        'user_events': user_events,
    }
    return render(request, 'boardgame/user_profile.html', context)