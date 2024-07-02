from django.shortcuts import render, get_object_or_404, redirect
from boardgame.models import GameSignup, Group,Event,GroupMembers,EventAttendance,GameNomination,Game
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
    members = group.members.all()
    is_member = members.filter(id=request.user.id).exists() 
    is_admin = GroupMembers.objects.filter(user=request.user, group=group, is_admin=True).exists()

    # Fetch events associated with the group
    events = Event.objects.filter(group=group).order_by('title')

    #Join Group and Request 
    if request.method == 'POST': # used when a form has been submitted, meaning someone clicked button 
        if 'join' in request.POST: # based on button name in html page
            if not is_member:
                GroupMembers.objects.create(user=request.user, group=group, is_admin=False)
        elif 'leave' in request.POST:
            if is_member:
                GroupMembers.objects.filter(user=request.user, group=group).delete()
        return redirect('group_profile', group_slug=group.slug)

    # Pass the group object to the template
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
    is_attending = attendees.filter(id=request.user.id).exists() #check to see if current user is attending

    nominations_with_slots = []
    for nomination in nominations:
        signed_up_count = GameSignup.objects.filter(nomination=nomination).count()
        remaining_slots = nomination.game.max_players - signed_up_count
        nominations_with_slots.append({
            'nomination': nomination,
            'remaining_slots': remaining_slots
        })

    if request.method == 'POST': # used when a form has been submitted, meaning someone clicked button 
        if 'join' in request.POST: # based on button name in html page
            if not is_attending:
                EventAttendance.objects.create(user=request.user, event=event) #create() will create and save object in one step
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
        return redirect('event_details', event_id=event_id)

    context = {
        'event': event,
        'attendees': attendees,
        'is_attending': is_attending,
        'nominations': nominations,
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
    is_attending = event.attendees.filter(id=request.user.id).exists()

    # Check if the user has already signed up for this game
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