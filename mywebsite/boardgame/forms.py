from django import forms 
from .models import Group,Event

# Create a group form
class GroupForm(forms.ModelForm):
    class Meta: 
        model = Group 
        fields = ('name','description','location')

# Create a group form
class EventForm(forms.ModelForm):
    class Meta: 
        model = Event 
        fields = ('title','description','date_time','location')

