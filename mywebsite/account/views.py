from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .forms import RegisterUserForm
from boardgame.forms import UserProfileForm 


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid login")

    return render(request, "registration/login.html")


def logout_user (request):
    logout(request)
    messages.success(request, "Logout successful")
    return redirect('home')

def register_user(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Automatically authenticate the user after registration
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            
            # Redirect to profile setup
            return redirect('profile_setup')
    else:
        form = RegisterUserForm()
    
    return render(request, 'registration/register_user.html', {'form': form})
