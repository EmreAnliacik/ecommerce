from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserLoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class UserSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='First name is required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Last name is required.')
    email = forms.EmailField(max_length=254, required=True, help_text='Enter a valid email address.')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')
