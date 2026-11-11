from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class SendMoneyForm(forms.Form):
    recipient_username = forms.CharField(max_length=150)
    amount = forms.DecimalField(max_digits=10, decimal_places=2)


class RequestMoneyForm(forms.Form):
    requested_from_username = forms.CharField(max_length=150)
    amount = forms.DecimalField(max_digits=10, decimal_places=2)


class AdminRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
