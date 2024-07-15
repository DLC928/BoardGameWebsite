from django import forms 
from .models import Group,Event, EventLocation, Game, UserProfile

# Create a group form
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name', 'description','group_image')
        labels = {
            'name': 'Group Name',
            'description': 'Group Description',
             'group_image': 'Group Image',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
        }
class EventForm(forms.ModelForm):
      class Meta:
        model = Event
        fields = ['title', 'description', 'date_time','event_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control', 'style': 'width: 50%;'}),
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
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}))
    picture = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file'}), required=False)

    class Meta:
        model = UserProfile
        fields = ['bio', 'picture']

        