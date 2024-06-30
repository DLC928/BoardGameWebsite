from django import forms 
from .models import Group,Event, EventLocation
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
 


class EventForm(forms.ModelForm):
    date_time = forms.SplitDateTimeField(widget=AdminSplitDateTime())

    class Meta:
        model = Event
        fields = ('title', 'description', 'date_time')

class EventLocationForm(forms.ModelForm):
    class Meta:
        model = EventLocation
        fields = ['name', 'address', 'city', 'postcode', 'country', 'latitude', 'longitude']
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }