from django import forms 
from .models import Category, Group,Event, EventLocation, Game, Tag, UserProfile

# Create a group form
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description','group_image','group_privacy','categories', 'tags']
        labels = {
            'name': 'Group Name',
            'description': 'Group Description',
            'group_privacy': 'Group Privacy',
            'group_image': 'Group Image',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'categories': forms.CheckboxSelectMultiple,
            'tags': forms.CheckboxSelectMultiple,
            'group_privacy': forms.RadioSelect()
        }
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date_time','event_image','categories', 'tags',
                  'nominations_open', 'signups_open']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control', 'style': 'width: 50%;'}),
            'categories': forms.CheckboxSelectMultiple,
            'tags': forms.CheckboxSelectMultiple,
            'nominations_open': forms.CheckboxInput(attrs={'class': 'form-check-input form-switch'}),
            'signups_open': forms.CheckboxInput(attrs={'class': 'form-check-input form-switch'}),
        }    

class EventNominationSettingsForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['nominations_open', 'signups_open']
        widgets = {
            'nominations_open': forms.CheckboxInput(attrs={'class': 'form-check-input form-switch'}),
            'signups_open': forms.CheckboxInput(attrs={'class': 'form-check-input form-switch'}),
        }    
        
class EventLocationForm(forms.ModelForm):
    class Meta:
        model = EventLocation
        fields = ['address', 'city', 'postcode', 'country', 'latitude', 'longitude']
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'postcode': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
        
class GameDetailForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['name', 'min_players', 'max_players', 'min_playtime', 'max_playtime', 'age', 'weight', 'description', 'thumbnail_url']
        widgets = {
            'name': forms.TextInput(attrs={'autocomplete': 'off', 'class': 'game-autocomplete'}),
            'min_players': forms.NumberInput(),
            'max_players': forms.NumberInput(),
            'min_playtime': forms.NumberInput(),
            'max_playtime': forms.NumberInput(),
            'age': forms.NumberInput(),
            'weight': forms.Textarea(),
            'description': forms.Textarea(),
            'thumbnail': forms.URLInput(),
        }
 
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'picture', 'favorite_games', 'categories', 'tags','city', 'state', 'country', 'latitude', 'longitude']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'style': 'width: 50%;'}),
            'favorite_games': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'style': 'width: 50%;'}),
            'picture': forms.FileInput(attrs={'class': 'form-control-file'}),
            'categories': forms.CheckboxSelectMultiple,
            'tags': forms.CheckboxSelectMultiple,
        }
        