from django import forms 
from .models import Group,Event, EventLocation, Game
from django.contrib.admin.widgets import  AdminDateWidget, AdminTimeWidget, AdminSplitDateTime

# Create a group form
class GroupForm(forms.ModelForm):
    class Meta: 
        model = Group 
        fields = ('name','description','location')

        labels = {
            'name': 'Group Name',
            'description': 'Group Description',
            'location': 'Group Location',
        }
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
        }
 


class EventForm(forms.ModelForm):
    date_time = forms.SplitDateTimeField(widget=AdminSplitDateTime())

    class Meta:
        model = Event
        fields = ('title', 'description', 'date_time')
        
    
    widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}), 
            'date_time': forms.SplitDateTimeWidget(attrs={'class': 'form-control'}),
        }    
        

class EventLocationForm(forms.ModelForm):
    class Meta:
        model = EventLocation
        fields = ['name', 'address', 'city', 'postcode', 'country', 'latitude', 'longitude']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
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
        fields = ['name', 'min_players', 'max_players', 'min_playtime', 'max_playtime', 'age', 'weight', 'description', 'thumbnail']
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


        