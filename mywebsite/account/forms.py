from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class RegisterUserForm(UserCreationForm): #the usercreationform is inherited into this custom form 
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control', 'style': 'width: 50%;'}))
    first_name = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'class':'form-control', 'style': 'width: 50%;'}))
    
    class Meta:
        model = User 
        fields = ('username','first_name','email','password1','password2')
        
    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'style': 'width: 50%;'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'style': 'width: 50%;'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'style': 'width: 50%;'})


