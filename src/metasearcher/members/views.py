from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import CustomUserForm, CustomAuthenticationForm

# Create your views here.
def login_user(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, ('You are now logged in!'))
            return redirect('/notifier/')
        else:
            messages.error(request, ("Username or password incorrect. Please try again."))
            return redirect('members:login')
    else:
        if request.user.is_authenticated:
            return redirect('releases_notifier:index')
        form = CustomAuthenticationForm()
        return render(request, 'registration/login.html', 
                      {
                          'form': form
                      })

def create_user(request):
    if request.method == "POST":
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("Registration Successful!"))
            return redirect('releases_notifier:index')
        else:
            messages.error(request, ('Some fields are not valid. See below.'))
    else:
        if request.user.is_authenticated:
            return redirect('releases_notifier:index')
        form = CustomUserForm()
    return render(request, 'registration/create_user.html',
                    {
                        'form': form
                    })

def logout_user(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            logout(request)
            prev_page = request.GET.get('next')
            messages.success(request, ("You were logged out. See you soon!"))
            if prev_page != None:
                return redirect(prev_page)
            
        else:
            redirect('members:login')
