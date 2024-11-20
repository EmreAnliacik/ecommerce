# forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='e-mail', max_length=150)
    password = forms.CharField(label='password', widget=forms.PasswordInput)
