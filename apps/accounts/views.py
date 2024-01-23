from django.shortcuts import render, redirect
from core.users_api_service import register_user, login_user, logout_user
from django.contrib import messages
from .forms import SignUpForm
from .actions.user_profile import do_create_user_profile

def logout_view(request):
    data = {}
    data['token'] = request.session['token']
    logout_user(data)
    request.session['token'] = None
    return redirect('/')

def register_view(request):
    msg = None
    success = False
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            data = {
            'username': request.POST['email'],
            'password': request.POST['password1'],
                 }
            response = register_user(data)
            if response.status_code == 201:
                success = True
                msg = 'User created successfully'
                request.session['email'] = data['username']
                request.session['token'] = response.json().get('token')
                user_id = response.json().get('user_id')
                profile = do_create_user_profile(user_id=user_id, country="IN")
                request.session['user_id'] = user_id
                request.session['user_profile_id'] = profile.id 
                #return redirect('index')
                msg = 'User registration successful. Please click Sign In.'
                success = True
            elif response.status_code == 400:
                error_data = response.json()
                if "username" in error_data:
                    form.add_error("email", error_data["username"][0])
                if "password" in error_data:
                    form.add_error("password", error_data["password"][0])
                msg = "There was a problem in registration. Please fix the errors and try again."
                success = False
        else:
            msg = 'There was problem with provided input. Please fix the errors and try again.'
            success = False
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})

def login_view(request):
    if request.method == 'POST':
        data = {
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
            # Add more fields as needed
        }
        response = login_user(data)
        if response['status'] == 'success':
            request.session['email'] = data['email']
            request.session['token'] = response.get('token')
            return redirect('index')
        else:
            messages.error(request, 'Login failed. Please try again.')
    else:
        return render(request, 'accounts/login.html')

def home_view(request):
    if request.method == 'POST':
        pass
    else:
        if request.session['token'] is None:
            return redirect('apps.accounts:login')
        else:
            token = request.session['token']
            return render(request, 'accounts/home.html')