from decimal import Decimal

import requests
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from conversion.views import calculate_conversion
from payapp.models import Account
from .forms import RegisterForm


BASELINE_GBP = Decimal('500')
CONVERSION_SERVICE_BASE = 'http://127.0.0.1:8000/webapps2026/conversion'


def get_opening_balance(currency):
    if currency == 'GBP':
        return BASELINE_GBP

    url = f'{CONVERSION_SERVICE_BASE}/GBP/{currency}/{BASELINE_GBP}/'
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            return Decimal(response.json()['converted_amount'])
    except (requests.RequestException, ValueError, KeyError):
        pass

    rate, converted = calculate_conversion('GBP', currency, BASELINE_GBP)
    return converted


def home(request):
    account = None
    if request.user.is_authenticated:
        account = Account.objects.filter(user=request.user).first()
    return render(request, 'register/home.html', {'account': account})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            currency = form.cleaned_data['currency']
            Account.objects.create(
                user=user,
                currency=currency,
                balance=get_opening_balance(currency),
            )
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'register/register.html', {'form': form})


def login_view(request):
    error_message = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        error_message = 'Invalid username or password'

    return render(request, 'register/login.html', {'error_message': error_message})


def logout_view(request):
    logout(request)
    return redirect('home')
