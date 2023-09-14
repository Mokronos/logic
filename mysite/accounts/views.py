from .forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_GET, require_POST


# Create your views here.

@require_GET
def home(request):
    base_template = "base.html"
    response = render(request, 'home.html', {'base_template': base_template})
    response['HX-Trigger'] = 'authAction'
    return response

@require_POST
def auth_login(request):

    # authenticate user
    data = request.POST
    form = AuthenticationForm(data=data)

    if form.is_valid():
        username = data['username']
        password = data['password']
        user = authenticate(
                request,
                username=username,
                password=password
                )
        if user is not None:
            login(request, user)
            print("login")
            base_template = "base.html"
            response = render(request, 'home.html', {'base_template': base_template})
            response['HX-Trigger'] = 'authAction'
            response['HX-Redirect'] = '/'
            return response
        else:
            return redirect('login')

@require_GET
def auth_login_form(request):
    print("auth_login_form_view")
    base_template = "base.html"

    if request.user.is_authenticated:
        print("user is authenticated and returning home page")
        response = render(request, 'home.html', {'base_template': base_template})
        return response

    else:
        print("user is not authenticated and returning login form")
        form = AuthenticationForm()
        response = render(request, 'accounts/login.html', {'form': form,
                                                           'base_template': base_template})
        return response

        
def auth_logout(request):
    print("auth_logout_view")

    print(f"csrf: {request.COOKIES['csrftoken']}")

    if request.htmx:
        base_template = "_partial.html"
    else:
        base_template = "base.html"

    if request.method == 'POST':
        # logout user
        logout(request)
        print("logout")
        print(f"base_template: {base_template}")
        response = render(request, 'home.html', {'base_template': base_template})
        response['HX-Trigger'] = 'authAction'
        response['HX-Redirect'] = '/'
        return response

def signup(request):
    print("signup_view")
    if request.htmx:
        base_template = "_partial.html"
    else:
        base_template = "base.html"
    # return signup form
    if request.method == 'GET':
        return render(request, 'accounts/signup.html', { 'form': CustomUserCreationForm,
                                                         'base_template': base_template})
    elif request.method == 'POST':
        # create new user
        print(f"POST: {request.body}")
        data = request.POST
        form = CustomUserCreationForm(data=data)
        if form.is_valid():
            form.save()

            return HttpResponse("You are signed up!")

def auth_bar(request):
    if request.htmx:
        print("auth_bar_view")
        # just refresh bar
        response = render(request, 'accounts/auth_bar.html')
        return response
    else:
        base_template = "base.html"
        response = render(request, 'home.html', {'base_template': base_template})
        return response

def debug(request):
    print("debug_view")
    return HttpResponse("debug")
