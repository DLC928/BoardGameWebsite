from datetime import datetime
from django.contrib import messages  

from django.shortcuts import render, get_object_or_404, redirect
from boardgame.models import User, Category, EventLocation, GameComment, GameSignup, Group,Event, GroupLocation,GroupMembers,EventAttendance,Game, Tag, UserProfile
from .forms import GroupForm, EventForm, EventLocationForm, GameDetailForm, UserProfileForm
from .utils import fetch_place_details
from django.db.models import Q
from django.views.generic import TemplateView


def home(request):
     # Fetch all groups and events with their locations
    group_list = Group.objects.all().select_related('grouplocation').order_by('name')
    event_list = Event.objects.all().select_related('eventlocation').order_by('title')

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

def group_profile(request, group_slug):
    # Retrieve the group object using the slug
    group = get_object_or_404(Group, slug=group_slug)
    members = group.members.all()

    # Determine if the user is authenticated and whether they are a member or admin
    is_member = False
    is_admin = False
    is_moderator = False
    if request.user.is_authenticated:
        is_member = members.filter(id=request.user.id).exists()
        is_admin = GroupMembers.objects.filter(user=request.user, group=group, is_admin=True).exists()
        is_moderator = GroupMembers.objects.filter(user=request.user, group=group, is_moderator=True).exists()

    # Fetch events associated with the group
    now = datetime.now()
    upcoming_events = Event.objects.filter(group=group, date_time__gte=now).order_by('date_time')
    past_events = Event.objects.filter(group=group, date_time__lt=now).order_by('-date_time')

    # Process join/leave group actions
    if request.method == 'POST' and request.user.is_authenticated:
        if 'join' in request.POST:
            if not is_member:
                GroupMembers.objects.create(user=request.user, group=group, is_admin=False)
        elif 'leave' in request.POST:
            if is_member:
                GroupMembers.objects.filter(user=request.user, group=group).delete()
        return redirect('group_profile', group_slug=group.slug)

    group_location = GroupLocation.objects.filter(group=group).first()
    # Pass the group object and related data to the template
    context = {
        'group': group,
        'group_location': group_location,
        'is_admin': is_admin,
        'is_moderator': is_moderator,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'members': members,
        'is_member': is_member,
    }
    return render(request, 'boardgame/group_profile.html', context)

def create_group(request):
    if request.method == 'POST':
        group_form = GroupForm(request.POST, request.FILES)
        if group_form.is_valid():
            group = group_form.save(commit=False)
            group.save()

            group_form.save_m2m()

            # Fetch place details using utility function
            place_id = request.POST.get('place_id')  # Get selected place ID
            place_details = fetch_place_details(place_id)

            if place_details:
                # Save location details to GroupLocation model or related model
                GroupLocation.objects.create(
                    group=group,
                    city=place_details['city'],
                    sublocality=place_details['sublocality'],
                    state=place_details['state'],
                    country=place_details['country'],
                    latitude=place_details['latitude'],
                    longitude=place_details['longitude'],
                )
            # Add user as a member of the group
            GroupMembers.objects.create(user=request.user, group=group, is_admin=True)

            # Redirect to group profile page
            return redirect('group_profile', group_slug=group.slug)
    else:
        group_form = GroupForm()
    
    return render(request, 'boardgame/create_group.html', {'form': group_form})

# ---------------------------EVENTS---------------------------

def create_event(request, group_slug):
    group = get_object_or_404(Group, slug=group_slug)
    event_form = EventForm(request.POST or None, request.FILES or None)
    location_form = None

    if request.method == 'POST':
        if event_form.is_valid():
            event = event_form.save(commit=False)
            event.group = group
            event.save()
            event_form.save_m2m()

            add_location = request.POST.get('add_location', False)

            if add_location == 'true':
                # Handle manual entry of location details
                location_form = EventLocationForm(request.POST)
                if location_form.is_valid():
                    event_location = location_form.save(commit=False)
                    event_location.event = event  # Associate event with event location
                    event_location.save()
            else:
                # Handle location details from Google Places API
                place_id = request.POST.get('place_id', None)
                if place_id:
                    place_details = fetch_place_details(place_id)

                    if place_details:
                        # Create EventLocation instance
                        EventLocation.objects.create(
                            event=event,
                            address=place_details.get('formatted_address', ''),
                            city=place_details.get('city', ''),
                            state=place_details.get('state', ''),
                            postcode=place_details.get('postcode', ''),
                            country=place_details.get('country', ''),
                            latitude=place_details.get('latitude', None),
                            longitude=place_details.get('longitude', None),
                        )

            return redirect('group_profile', group_slug=group_slug)
    
    context = {
        'form': event_form,
        'location_form': location_form,
        'group': group,
    }
    return render(request, 'boardgame/create_event.html', context)

def event_details(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    attendees = event.attendees.all()
    nominations = Game.objects.filter(event=event)
    
    is_attending = False
    if request.user.is_authenticated:
        is_attending = attendees.filter(id=request.user.id).exists()

    nominations_with_slots = []
    waitlisted_games = []
    for nomination in nominations:
        signed_up_count = GameSignup.objects.filter(nomination=nomination).count()
        remaining_slots = nomination.max_players - signed_up_count
        players_needed = max(0, nomination.min_players - signed_up_count)
        
        is_signed_up = False
        if request.user.is_authenticated:
            is_signed_up = GameSignup.objects.filter(nomination=nomination, user=request.user).exists()
        
        if remaining_slots > 0:
            nominations_with_slots.append({
                'nomination': nomination,
                'remaining_slots': remaining_slots,
                'is_signed_up': is_signed_up,
                'signed_up_count':signed_up_count,
                'players_needed': players_needed
            })
        else:
            waitlisted_games.append({
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
            nomination = get_object_or_404(Game, id=nomination_id)
            if is_attending and not GameSignup.objects.filter(nomination=nomination, user=request.user).exists():
                GameSignup.objects.create(nomination=nomination, user=request.user)
        
        elif 'leave_game' in request.POST:
            nomination_id = request.POST.get('nomination_id')
            nomination = get_object_or_404(Game, id=nomination_id)
            if GameSignup.objects.filter(nomination=nomination, user=request.user).exists():
                if nomination.nominator == request.user:
                    GameSignup.objects.filter(nomination=nomination).delete()
                    nomination.delete()
                    return redirect('event_details', event_id=event_id)
                else:
                    GameSignup.objects.filter(nomination=nomination, user=request.user).delete()
             
        elif 'remove_nomination' in request.POST:
            nomination_id = request.POST.get('nomination_id')
            nomination = get_object_or_404(Game, id=nomination_id)
            if nomination.nominator == request.user:
                GameSignup.objects.filter(nomination=nomination).delete()
                nomination.delete()
        
        return redirect('event_details', event_id=event_id)

    event_location = EventLocation.objects.filter(event=event).first()

    context = {
        'event': event,
        'event_location': event_location,
        'is_attending': is_attending,
        'nominations': nominations,
        'waitlisted_games': waitlisted_games,
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
            game.event = event
            game.nominator = request.user
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
            
            # Automatically set thumbnail if available
            game.thumbnail_url = request.POST.get('thumbnail')
            game.save()
            
            # Create GameSignup for the user who nominated the game
            GameSignup.objects.create(nomination=game, user=request.user)

            return redirect('event_details', event_id=event_id)
    else:
        form = GameDetailForm()
    
    return render(request, 'boardgame/nominate_game.html', {'form': form, 'event': event})

def game_details(request, event_id, game_id):
    event = get_object_or_404(Event, id=event_id)
    game = get_object_or_404(Game, id=game_id)
    
    is_attending = False
    is_signed_up = False
    if request.user.is_authenticated:
        is_attending = event.attendees.filter(id=request.user.id).exists()
        is_signed_up = GameSignup.objects.filter(nomination=game, user=request.user).exists()

    # Calculate remaining sign-up slots
    signed_up_count = GameSignup.objects.filter(nomination=game).count()
    remaining_slots = game.max_players - signed_up_count

    # Retrieve the list of players signed up for this game
    game_signup_set = GameSignup.objects.filter(nomination=game)

    if request.method == 'POST':
        if 'sign_up' in request.POST:
            if not is_signed_up:
                # Create a new GameSignup entry for the current user
                GameSignup.objects.create(nomination=game, user=request.user)
        elif 'leave' in request.POST:
            if is_signed_up:
                # Check if the user is the nominator
                if game.nominator == request.user:
                    # Remove all signups for this nomination
                    GameSignup.objects.filter(nomination=game).delete()
                    # Remove the nomination itself
                    game.delete()
                    # Redirect to event details if the nominator leaves
                    return redirect('event_details', event_id=event_id)
                else:
                    # Remove the GameSignup entry for the current user
                    GameSignup.objects.filter(nomination=game, user=request.user).delete()
        elif 'comment' in request.POST:
            comment_content = request.POST.get('comment_content')
            if comment_content:
                GameComment.objects.create(nominated_game=game, user=request.user, content=comment_content)

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


def profile_setup(request):
    user_profile = UserProfile.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user  # Associate profile with current logged-in user
            profile.save()
            return redirect('home')  # Redirect to home or profile view
    else:
        profile_form = UserProfileForm(instance=user_profile)
    
    return render(request, 'boardgame/profile_setup.html', {'profile_form': profile_form})

# ---------------------------NAVBAR---------------------------

def groups(request):
    tag_name = request.GET.get('tag')
    category_name = request.GET.get('category')
    show_user_groups = request.GET.get('your_groups') == 'true'
    search_query = request.GET.get('search')
    
    # Get all groups
    group_list = Group.objects.all().order_by('name')
    
    # Filter by search query if present
    if search_query:
        # Filter by group name or location
        group_list = group_list.filter(
            Q(name__icontains=search_query) |
            Q(grouplocation__city__icontains=search_query) |
            Q(grouplocation__sublocality__icontains=search_query)
        ).distinct()

    # Filter by tag if a tag is specified
    if tag_name:
        group_list = group_list.filter(tags__name=tag_name)

    # Filter by category if a category is specified
    if category_name:
        group_list = group_list.filter(categories__name=category_name)

    # Filter user groups if 'your_groups' is specified or if user is authenticated
    user_groups = None
    user = request.user
    if show_user_groups and user.is_authenticated:
        user_groups = GroupMembers.objects.filter(user=user).select_related('group')
        if show_user_groups:
            group_list = group_list.filter(id__in=user_groups.values_list('group_id', flat=True))

    context = {
        'groups': group_list,
        'user_groups': user_groups,
        'tags': Tag.objects.all(),
        'categories': Category.objects.all(),
        'search_query': search_query, 
    }
    return render(request, 'boardgame/groups.html', context=context)


def events(request):
    tag_name = request.GET.get('tag')
    category_name = request.GET.get('category')
    show_user_events = request.GET.get('your_events') == 'true'
    search_query = request.GET.get('search')
    
    now = datetime.now()
    # Get upcoming events
    event_list = Event.objects.filter(date_time__gte=now).order_by('title')
    
      # Filter by search query if present
    if search_query:
        # Filter by group name or location
        event_list = event_list.filter(
            Q(title__icontains=search_query) |
            Q(eventlocation__city__icontains=search_query) 
        ).distinct()

    # Filter by tag if a tag is specified
    if tag_name:
        event_list = event_list.filter(tags__name=tag_name,date_time__gte=now)

    # Filter by category if a category is specified
    if category_name:
        event_list = event_list.filter(categories__name=category_name,date_time__gte=now)

    # Filter user events if 'your_events' is specified and if user is authenticated
    user_events = None
    user = request.user
    if show_user_events and user.is_authenticated:
        user_events = EventAttendance.objects.filter(user=user).select_related('event')
        if show_user_events:
            event_list = event_list.filter(id__in=user_events.values_list('event_id', flat=True))

    context = {
        'events': event_list,
        'tags': Tag.objects.all(),
        'categories': Category.objects.all(),
        'search_query': search_query, 
    }
    return render(request, 'boardgame/events.html', context=context)

def search(request):
    if request.method == "POST":
        searched = request.POST.get('searched')
        group_locations = GroupLocation.objects.filter(
            Q(city__icontains=searched) | Q(sublocality__icontains=searched)
        )

        groups = Group.objects.filter(
            Q(grouplocation__city__icontains=searched) | 
            Q(grouplocation__sublocality__icontains=searched)
        ).distinct()

        event_locations = EventLocation.objects.filter(
            Q(city__icontains=searched) | Q(sublocality__icontains=searched)
        )

        events = Event.objects.filter(
            Q(eventlocation__city__icontains=searched) | 
            Q(eventlocation__sublocality__icontains=searched)
        ).distinct()

        return render(request, 'boardgame/search.html', {
            'searched': searched, 
            'group_locations': group_locations, 
            'groups': groups,
            'event_locations': event_locations,
            'events': events
        })
    
    return render(request, 'boardgame/search.html', {})

def admin_dashboard(request, group_slug,section=None):
    group = get_object_or_404(Group, slug=group_slug)
    section = section or request.GET.get('section', 'member_management')

    if section == 'member_management':
        if request.method == 'POST':
            action = request.POST.get('action')
            user_id = request.POST.get('user_id')
            selected_user = User.objects.get(id=user_id)
            group_member = GroupMembers.objects.get(user=selected_user, group=group)
            
            if action == 'set_admin':
                group_member.is_admin = True
                group_member.save()
                messages.success(request, f"{selected_user.username} has been changed to admin.")   
            elif action == 'set_mod':
                group_member.is_moderator = True
                group_member.save() 
                messages.success(request, f"{selected_user.username} has been changed to moderator.")     
            elif action == 'remove_mod':
                if GroupMembers.objects.filter(group=group, is_moderator=True):
                    group_member.is_moderator = False
                    group_member.save()
                    messages.success(request, f"{selected_user.username} has been removed as moderator.")    
            elif action == 'remove_admin':
                if GroupMembers.objects.filter(group=group, is_admin=True).count() > 1:
                    group_member.is_admin = False
                    group_member.save()
                    messages.success(request, f"{selected_user.username} has been removed as admin.")
                else:
                    messages.error(request, f"You are the last admin of {group.name}. Invite new admins to maintain this group when you're not an admin.")

            return redirect('admin_dashboard', group_slug=group.slug)
        
        admins = GroupMembers.objects.filter(group=group, is_admin=True)
        moderators = GroupMembers.objects.filter(group=group, is_moderator=True)
        users = GroupMembers.objects.filter(group=group, is_admin=False, is_moderator=False)
        context = {'admins': admins, 'moderators': moderators, 'users': users, 'group': group}
        
    elif section == 'event_management':
        if request.method == 'POST':
            action = request.POST.get('action')
            event_id = request.POST.get('event_id')
            event = get_object_or_404(Event, pk=event_id)
            if action == 'delete':
                event.delete()
                messages.success(request, "Event deleted successfully.")
            elif action == 'edit_event':
                form = EventForm(request.POST, instance=event)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Event updated successfully.")
            return redirect('admin_dashboard_with_section', group_slug=group.slug, section='event_management')
        

        now = datetime.now()
        upcoming_events = Event.objects.filter(group=group, date_time__gte=now).order_by('date_time')
        past_events = Event.objects.filter(group=group, date_time__lt=now).order_by('-date_time')
        # Create a form for each upcoming event
        forms = {event.id: EventForm(instance=event).as_p() for event in upcoming_events}
        
        context = {'upcoming_events': upcoming_events, 'past_events':past_events, 'group': group, 'forms': forms}
        
    elif section == 'game_management':
        if request.method == 'POST':
            nomination_id = request.POST.get('nomination_id')
            action = request.POST.get('action')
            nomination = get_object_or_404(Game, id=nomination_id)
            if action == 'approve':
                nomination.status = 'approved'
            elif action == 'reject':
                nomination.status = 'rejected'
            nomination.save()
            return redirect('admin_dashboard', group_slug=group.slug, section='game_management')

        nominations = '' #will fix later
        context = {'nominations': nominations, 'group': group}

    elif section == 'notification_management':
        if request.method == 'POST':
            # Handle sending notifications
            pass

        notifications = []  # Adding logic later
        context = {'notifications': notifications, 'group': group}

    elif section == 'group_management':
        if request.method == 'POST':
            group_id = request.POST.get('group_id')
            action = request.POST.get('action')
            group = get_object_or_404(Group, id=group_id)
            if action == 'edit':
                # Handle editing logic 
                pass
            elif action == 'remove':
                group.delete()
            return redirect('admin_dashboard', group_slug=group.slug, section='group_management')

        groups = Group.objects.all()
        context = {'groups': groups, 'group': group}

    else:
        context = {'group': group}

    context['section'] = section
    return render(request, 'boardgame/admin_dashboard.html', context)



def edit_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    form = EventForm(request.POST or None, instance=event)
    
    if form.is_valid():
        form.save()
        return redirect('event_details', event_id=event_id)

    return render(request, 'boardgame/edit_event.html', {'form': form, 'event': event})
