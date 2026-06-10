from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

# Create your views here.


def login_view(request):
    if request.user.is_authenticated:
        return role_redirect(request.user)

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return role_redirect(user)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def role_redirect(user):
    if user.role == 'admin':
        return redirect('/admin-panel/dashboard/')
    elif user.role == 'teacher':
        return redirect('/teacher/dashboard/')
    elif user.role == 'student':
        return redirect('/student/dashboard/')
    return redirect('/accounts/login/')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('/accounts/login/')