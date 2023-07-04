from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm
from apps.accounts.models import User


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Имя пользователя"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Пароль"
    )


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            'email',
        ]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class":"form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }



class UserProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = [
            'username',
            'last_name',
            'first_name',
            'date_of_birth',
            'gender',
            'email',
            'image'
            ]
        widgets = {
            # "username": forms.TextInput(attrs={"class": "form-control"}),
            # "email": forms.EmailInput(attrs={"class":"form-control"}),
            # "first_name": forms.TextInput(attrs={"class": "form-control"}),
            # "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "media": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }