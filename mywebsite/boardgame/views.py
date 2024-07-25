from datetime import datetime
from django.contrib import messages 
from django.http import HttpResponseRedirect 
from django.shortcuts import render, redirect
from boardgame.models import EventPost, GroupPost, User, Category, EventLocation, GameComment, GameSignup, Group,Event, GroupLocation,GroupMembers,EventAttendance,Game, Tag, UserProfile, Vote
from .forms import EventCommentForm, EventNominationSettingsForm, EventPostForm, GroupCommentForm, GroupForm, EventForm, EventLocationForm, GameDetailForm, GroupPostForm, UserProfileForm
from .utils import fetch_place_details
from django.db.models import Count, Q

def home(request):
    now = datetime.now()
    group_list = Group.objects.all().select_related('grouplocation').order_by('name')
    event_list = Event.objects.filter(date_time__gte=now).select_related('eventlocation').order_by('title')
    # Initialize user-related variables
    user_groups = None
    user_events = None
    user_profile = None
    user = request.user
    recommended_groups = []

    if user.is_authenticated:
        # Fetch user-specific groups and events
        user_groups = GroupMembers.objects.filter(user=user).select_related('group')
        user_events = EventAttendance.objects.filter(user=user, event__date_time__gte=now).select_related('event')
        user_profile = UserProfile.objects.get(user=user)
        
        if user_profile:
            city = user_profile.city
            if city: 
                all_recommendations = Group.objects.filter(grouplocation__city=city)
                joined_groups = user_groups.values_list('group_id', flat=True)
                recommended_groups = all_recommendations.exclude(id__in=joined_groups)
    context = {
        'groups': group_list,
        'events': event_list,
        'user_groups': user_groups,
        'user_events': user_events,
        'user_profile':user_profile,
        'recommended_groups':recommended_groups,
    }
    return render(request, 'boardgame/home.html', context=context)
# ---------------------------GROUPS---------------------------
def group_profile(request, group_slug):
    group = Group.objects.get(slug=group_slug)
    members = group.members.all()
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
    post_form = GroupPostForm()
    comment_form = GroupCommentForm()
    # Process join/leave group actions
    if request.method == 'POST' and request.user.is_authenticated:
        if 'join' in request.POST:
            if not is_member:
                GroupMembers.objects.create(user=request.user, group=group, is_admin=False)
        elif 'leave' in request.POST:
            if is_member:
                GroupMembers.objects.filter(user=request.user, group=group).delete()
        elif 'post_content' in request.POST:
                post_form = GroupPostForm(request.POST)
                if post_form.is_valid():
                    post = post_form.save(commit=False)
                    post.group = group
                    post.user = request.user
                    post.save()
        elif 'comment_content' in request.POST:
                comment_form = GroupCommentForm(request.POST)
                post_id = request.POST.get('post_id')
                if post_id and comment_form.is_valid():
                    comment = comment_form.save(commit=False)
                    comment.post_id = post_id
                    comment.user = request.user
                    comment.save()
        return redirect('group_profile', group_slug=group.slug)
    group_location = GroupLocation.objects.filter(group=group).first()
    posts = GroupPost.objects.filter(group=group).order_by('-date_added')
    context = {
        'group': group,
        'group_location': group_location,
        'is_admin': is_admin,
        'is_moderator': is_moderator,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'members': members,
        'is_member': is_member,
        'post_form': post_form,
        'comment_form': comment_form,
        'posts': posts,
    }
    return render(request, 'boardgame/group_profile.html', context)

def create_group(request):
    if request.method == 'POST':
        group_form = GroupForm(request.POST, request.FILES)
        if group_form.is_valid():
            group = group_form.save(commit=False)
            group.save()
            group_form.save_m2m() #For tags and categories 
            
            # Fetch place details using utility function
            place_id = request.POST.get('place_id')  # Get selected place ID
            place_details = fetch_place_details(place_id)

            if place_details:
                # Save location details to GroupLocation model
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
            return redirect('group_profile', group_slug=group.slug)
    else:
        group_form = GroupForm()
    
    return render(request, 'boardgame/create_group.html', {'form': group_form})

# ---------------------------EVENTS---------------------------
def create_event(request, group_slug):
    group = Group.objects.get(slug=group_slug)
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
    event = Event.objects.get(id=event_id)
    attendees = event.attendees.all()
    nominations = Game.objects.filter(event=event)
    approved_nominations = Game.objects.filter(event=event, nomination_status='Approved')
    event_location = EventLocation.objects.filter(event=event).first()
    
    # Initialize context variables
    is_attending = is_admin = is_moderator = has_nomination = False
    vote_counts = {}
    user_votes = total_user_votes = 0

    if request.user.is_authenticated:
        is_attending = attendees.filter(id=request.user.id).exists()
        is_admin = GroupMembers.objects.filter(user=request.user, group=event.group, is_admin=True).exists()
        is_moderator = GroupMembers.objects.filter(user=request.user, group=event.group, is_moderator=True).exists()
        has_nomination = Game.objects.filter(event=event, nominator=request.user).exists()
        # Calculate vote counts for each game
        vote_counts = {nomination.id: Vote.objects.filter(game=nomination, event=event).count() for nomination in nominations}
        user_votes = Vote.objects.filter(user=request.user, event=event).values_list('game_id', flat=True)
        total_user_votes = Vote.objects.filter(user=request.user, event=event).count()
    
    approved_nominations_with_slots = []
    waitlisted_games = []
    for nomination in approved_nominations:
        signed_up_count = GameSignup.objects.filter(nomination=nomination).count()
        remaining_slots = nomination.max_players - signed_up_count
        players_needed = max(0, nomination.min_players - signed_up_count)
        
        is_signed_up = False
        if request.user.is_authenticated:
            is_signed_up = GameSignup.objects.filter(nomination=nomination, user=request.user).exists()
        
        if remaining_slots > 0:
            approved_nominations_with_slots.append({
                'nomination': nomination,
                'remaining_slots': remaining_slots,
                'is_signed_up': is_signed_up,
                'signed_up_count': signed_up_count,
                'players_needed': players_needed
            })
        else:
            waitlisted_games.append({
                'nomination': nomination,
                'remaining_slots': remaining_slots,
                'is_signed_up': is_signed_up
            })
    if request.method == 'POST':
        if request.user.is_authenticated:
            if 'join' in request.POST:
                if not is_attending:
                    EventAttendance.objects.create(user=request.user, event=event)
            elif 'leave' in request.POST:
                if is_attending:
                    EventAttendance.objects.filter(user=request.user, event=event).delete()
                    for nomination in nominations:
                        GameSignup.objects.filter(user=request.user, nomination=nomination).delete()
                        if nomination.nominator == request.user:
                            GameSignup.objects.filter(nomination=nomination).delete()
                            nomination.delete()
            elif 'sign_up' in request.POST:
                nomination_id = request.POST.get('nomination_id')
                nomination = Game.objects.get(id=nomination_id)
                if is_attending and not GameSignup.objects.filter(nomination=nomination, user=request.user).exists():
                    GameSignup.objects.create(nomination=nomination, user=request.user)
            elif 'leave_game' in request.POST:
                nomination_id = request.POST.get('nomination_id')
                nomination = Game.objects.get(id=nomination_id)
                if GameSignup.objects.filter(nomination=nomination, user=request.user).exists():
                    if nomination.nominator == request.user:
                        GameSignup.objects.filter(nomination=nomination).delete()
                        nomination.delete()
                        return redirect('event_details', event_id=event_id)
                    else:
                        GameSignup.objects.filter(nomination=nomination, user=request.user).delete()
            elif 'post_content' in request.POST:
                post_form = EventPostForm(request.POST)
                if post_form.is_valid():
                    post = post_form.save(commit=False)
                    post.event = event
                    post.user = request.user
                    post.save()
                    return redirect('event_details', event_id=event_id)
            elif 'comment_content' in request.POST:
                comment_form = EventCommentForm(request.POST)
                post_id = request.POST.get('post_id')
                if post_id and comment_form.is_valid():
                    comment = comment_form.save(commit=False)
                    comment.post_id = post_id
                    comment.user = request.user
                    comment.save()
                    return redirect('event_details', event_id=event_id)
            elif 'has_nomination' in request.POST:
                if has_nomination:
                    messages.error(request, "You have already nominated a game. You can only nominate one game.")
            
            elif 'remove_nomination' in request.POST:
                nomination_id = request.POST.get('nomination_id')
                nomination = Game.objects.get(id=nomination_id)
                if nomination.nominator == request.user:
                    GameSignup.objects.filter(nomination=nomination).delete()
                    nomination.delete()
            
            elif 'vote' in request.POST:
                nomination_id = request.POST.get('nomination_id')
                nomination = Game.objects.get(id=nomination_id)
                if not Vote.objects.filter(user=request.user, game=nomination, event=event).exists():
                    if Vote.objects.filter(user=request.user, event=event).count() < 3:
                        Vote.objects.create(user=request.user, game=nomination, event=event)
            
            elif 'remove_vote' in request.POST:
                nomination_id = request.POST.get('nomination_id')
                nomination = Game.objects.get(id=nomination_id)
                if Vote.objects.filter(user=request.user, game=nomination, event=event).exists():
                    Vote.objects.filter(user=request.user, game=nomination, event=event).delete()
            
            return redirect('event_details', event_id=event_id)
        
    post_form = EventPostForm()
    comment_form = EventCommentForm()
    posts = EventPost.objects.filter(event=event).order_by('-date_added')
    
    context = {
        'event': event,
        'event_location': event_location,
        'is_attending': is_attending,
        'is_admin': is_admin,
        'is_moderator': is_moderator,
        'nominations': nominations,
        'waitlisted_games': waitlisted_games,
        'attendees': attendees,
        'approved_nominations_with_slots': approved_nominations_with_slots,
        'vote_counts': vote_counts,
        'user_votes': user_votes,
        'total_user_votes': total_user_votes,
        'has_nomination': has_nomination,
        'post_form': post_form,
        'comment_form': comment_form,
        'posts': posts,
    }

    return render(request, 'boardgame/event_details.html', context)


def nominate_game(request, event_id):
    event = Event.objects.get(id=event_id)
    if request.method == 'POST':
        form = GameDetailForm(request.POST)
        if form.is_valid():
            game = form.save(commit=False)
            game.event = event
            game.nominator = request.user
            game.name = request.POST.get('name')
            game.description = request.POST.get('description')
            
            # Check if the game already exists for the event
            if Game.objects.filter(event=event, name=game.name).exists():
                messages.error(request, 'This game has already been nominated for the event.')
                return HttpResponseRedirect(request.path_info)  # Redirect to the same page to show the error message
            
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
    event = Event.objects.get(id=event_id)
    game = Game.objects.get(id=game_id)
    
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

def user_profile(request,id):
    user = User.objects.get(id=id)
    user_profile = UserProfile.objects.filter(user=user).first()  
    user_groups = GroupMembers.objects.filter(user=user).select_related('group')
    user_events = EventAttendance.objects.filter(user=user).select_related('event')
    
    context = {
        'user': user,
        'user_profile': user_profile,
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
            
            # Save ManyToMany relationships for category and tags
            profile_form.save_m2m()

            # Fetch place details using utility function
            place_id = request.POST.get('place_id')  # Get selected place ID
            place_details = fetch_place_details(place_id)

            if place_details:
                # Update location details to UserProfile model
                profile.city = place_details['city']
                profile.state = place_details['state']
                profile.country = place_details['country']
                profile.latitude = place_details['latitude']
                profile.longitude = place_details['longitude']
                profile.save()
                
            return redirect('home')  # Redirect to home 
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

def manage_group_dashboard(request, group_slug, section=None):
    group = Group.objects.get(slug=group_slug)
    section = section or request.GET.get('section', 'group_setup')
    # Fetch the group location
    group_location = None
    if GroupLocation.objects.filter(group=group).exists():
        group_location = GroupLocation.objects.get(group=group)
    
    context = {'group': group, 'section': section}
    
    if section == 'group_setup':
        if request.method == 'POST':
            form = GroupForm(request.POST, instance=group)
            if form.is_valid():
                form.save()
                # Fetch place details using utility function if place_id is provided
                place_id = request.POST.get('place_id')
                if place_id:
                    place_details = fetch_place_details(place_id)
                    if place_details:
                        if group_location is None:
                            group_location = GroupLocation(group=group)
                        group_location.city = place_details.get('city', '')
                        group_location.sublocality = place_details.get('sublocality', '')
                        group_location.state = place_details.get('state', '')
                        group_location.postcode = place_details.get('postcode', '')
                        group_location.country = place_details.get('country', '')
                        group_location.latitude = place_details.get('latitude', None)
                        group_location.longitude = place_details.get('longitude', None)
                        group_location.save()

                messages.success(request, 'Group updated successfully.')
                return redirect('manage_group_dashboard_with_section', group_slug=group.slug, section='group_setup')
        else:
            form = GroupForm(instance=group)
            
        context.update({'form': form,'current_location': group_location})

    elif section == 'event_management':
        if request.method == 'POST':
            action = request.POST.get('action')
            event_id = request.POST.get('event_id')
            
            if action == 'delete_Event':
                event = Event.objects.get(id=event_id)
                event.delete()
                messages.success(request, 'Group successfully deleted.')
                return redirect('manage_group_dashboard_with_section', group_slug=group.slug, section='event_management')
        now = datetime.now()
        upcoming_events = Event.objects.filter(group=group, date_time__gte=now).order_by('date_time')
        past_events = Event.objects.filter(group=group, date_time__lt=now).order_by('-date_time')
        
        context.update({'upcoming_events': upcoming_events, 'past_events': past_events})
          
    elif section == 'member_management':
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

            return redirect('manage_group_dashboard_with_section', group_slug=group.slug, section='member_management')
        
        admins = GroupMembers.objects.filter(group=group, is_admin=True)
        moderators = GroupMembers.objects.filter(group=group, is_moderator=True)
        users = GroupMembers.objects.filter(group=group, is_admin=False, is_moderator=False)
        context.update({'admins': admins, 'moderators': moderators, 'users': users})
    return render(request, 'boardgame/manage_group_dashboard.html', context)

def manage_event_dashboard(request, event_id, section=None):
    event = Event.objects.get(id=event_id)
    section = section or request.GET.get('section', 'event_setup')
    
    event_location = None
    if EventLocation.objects.filter(event=event).exists():
        event_location = EventLocation.objects.get(event=event)
    
    context = {'event': event, 'section': section}

    if section == 'event_setup':
        if request.method == 'POST':
            form = EventForm(request.POST, instance=event)
            
            if form.is_valid():
                form.save()
                # Fetch place details using utility function if place_id is provided
                place_id = request.POST.get('place_id')
                if place_id:
                    place_details = fetch_place_details(place_id)
                    if place_details:
                        if event_location is None:
                            event_location = EventLocation(event=event)
                        event_location.address = place_details.get('formatted_address', '')
                        event_location.city = place_details.get('city', '')
                        event_location.state = place_details.get('state', '')
                        event_location.postcode = place_details.get('postcode', '')
                        event_location.country = place_details.get('country', '')
                        event_location.latitude = place_details.get('latitude', None)
                        event_location.longitude = place_details.get('longitude', None)
                        event_location.save()
                messages.success(request, 'Event updated successfully.')
                return redirect('manage_event_dashboard_with_section', event_id=event.id, section='event_setup')
        else:
            form = EventForm(instance=event)
        
        context.update({'form': form,'event_location':event_location})
        
    elif section == 'game_nominations':
        if request.method == 'POST':
            action = request.POST.get('action')
            nomination_id = request.POST.get('nomination_id')

            if action and nomination_id:
                nomination = Game.objects.get(id=nomination_id)

                if action == 'approve':
                    nomination.nomination_status = 'Approved'
                    nomination.save()
                    messages.success(request, 'Game nomination approved.')
                elif action == 'reject':
                    nomination.nomination_status = 'Rejected'
                    nomination.save()
                    messages.success(request, 'Game nomination rejected.')
                elif action == 'delete':
                    nomination.delete()
                    messages.success(request, 'Game nomination deleted.')

                return redirect('manage_event_dashboard_with_section', event_id=event.id, section='game_nominations')

            elif 'nomination_settings' in request.POST:
                nomination_settings = EventNominationSettingsForm(request.POST, instance=event)
                if nomination_settings.is_valid():
                    nomination_settings.save()
                    messages.success(request, 'Event settings updated successfully.')
                    return redirect('manage_event_dashboard_with_section', event_id=event.id, section='game_nominations')

        nominations = Game.objects.filter(event=event) 
              
        pending_nominations = Game.objects.filter(
            event=event, 
            nomination_status='Pending'
        ).annotate(
            vote_count=Count('vote', filter=Q(vote__event=event))
        ).order_by('-vote_count')

        approved_nominations = Game.objects.filter(event=event, nomination_status='Approved')
        rejected_nominations = Game.objects.filter(event=event, nomination_status='Rejected')

        # Calculate vote counts for each game
        vote_counts = {}
        for nomination in nominations:
            count = Vote.objects.filter(game=nomination, event=event).count()
            vote_counts[nomination.id] = count
        nomination_settings = EventNominationSettingsForm(instance=event)
        context.update({'pending_nominations': pending_nominations, 'approved_nominations': approved_nominations,
                        'vote_counts': vote_counts, 'nomination_settings': nomination_settings,'rejected_nominations':rejected_nominations})
    
    elif section == 'attendee_management':
        attendees = event.attendees.all()
        if request.method == 'POST':
            action = request.POST.get('action')
            user_id = request.POST.get('user_id')
            selected_user = User.objects.get(id=user_id)
            
            if action == 'remove':
                event.attendees.remove(selected_user)
                messages.success(request, f"{selected_user.username} has been removed from the event.")
            
            return redirect('manage_event_dashboard_with_section', event_id=event.id, section='attendee_management')     
        context.update({'attendees': attendees})
    return render(request, 'boardgame/manage_event_dashboard.html', context)






                        