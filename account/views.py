from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.conf import settings
from account.form import RegistrationForm, LoginForm
from account.models import Account


def register_view(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        return HttpResponse(f"You are already authenticated {user.email}")
    context = {}

    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email').lower()
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(email=email, password=raw_password)
            login(request, account)
            # destination = kwargs.get('next')
            destination = get_redirect_if_exists(request)
            if destination:
                return redirect(destination)
            return redirect("home")
        else:
            context['registration_form'] = form

    return render(request, 'account/register.html', context)


def login_view(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        # return HttpResponse(f"You are already authenticated {user.email}")
        return redirect('home')
    context = {}

    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                destination = get_redirect_if_exists(request)
                if destination:
                    return redirect(destination)
                return redirect('home')
        else:
            # send error to the view if any
            context['login_form'] = form

    return render(request, 'account/login.html', context)


def get_redirect_if_exists(request):
    redirect = None
    if request.GET:
        if request.GET.get('next'):
            redirect = str(request.GET.get('next'))

    return redirect


def logout_view(request):
    logout(request)
    return redirect('home')


def account_view(request, *args, **kwargs):
    """

    is_self:
        is_friend:
            -1: NO_REQUEST_SENT
            0: THEM_SENT_TO_YOU
            1: YOU_SENT_TO_THEM

    """
    context = {}
    user_id = kwargs.get('user_id')
    try:
        # Get user we are viewing
        account = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        return HttpResponse("User Id doesn't exist")
    if account:
        context['id'] = account.id
        context['username'] = account.username
        context['email'] = account.email
        context['profile_image'] = account.profile_image
        context['hide_email'] = account.hide_email

        # define state variable
        is_self = True
        is_friend = False
        user = request.user
        # view logic here
        if user.is_authenticated and user != account:
            is_self = False
        elif not user.is_authenticated:
            is_self = False

        context["is_self"] = is_self
        context["is_friend"] = is_friend
        context["BASE_URL"] = settings.BASE_URL

        return render(request,"account/account.html",context)
