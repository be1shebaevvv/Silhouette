import re

from django import forms
from django.contrib.auth.forms import PasswordResetForm, UserChangeForm, UserCreationForm

from apps.accounts.models import User


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Никнейм",
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "username"}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "current-password"}),
    )


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        label="Никнейм",
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "username", "maxlength": 150}),
    )
    email = forms.EmailField(
        label="Электронная почта для подтверждения (не отображается в профиле)",
        widget=forms.EmailInput(attrs={"class": "form-control", "autocomplete": "email"}),
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Повторите пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ["username", "email"]


class UserProfileForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ["username", "email", "image"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "autocomplete": "username", "maxlength": 150}),
            "email": forms.EmailInput(attrs={"class": "form-control", "autocomplete": "email"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".jpg,.jpeg,.png,.webp"}),
        }
        labels = {
            "username": "Публичный никнейм",
            "email": "Электронная почта (не отображается в профиле)",
            "image": "Аватар (необязательно)",
        }

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if not re.fullmatch(r"[A-Za-z0-9_]+", username):
            raise forms.ValidationError("Используйте английские буквы, цифры и знак подчёркивания.")
        return username

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and hasattr(image, "size"):
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Размер аватара не должен превышать 5 МБ.")
            extension = image.name.rsplit(".", 1)[-1].lower() if "." in image.name else ""
            if extension not in {"jpg", "jpeg", "png", "webp"}:
                raise forms.ValidationError("Разрешены аватары JPG, PNG и WebP.")
        return image


class DeleteAccountForm(forms.Form):
    password = forms.CharField(
        label="Текущий пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "current-password"}),
    )



class VerifiedPasswordResetForm(PasswordResetForm):
    """Only send password-reset links to verified accounts."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({"class": "form-control", "autocomplete": "email"})

    def get_users(self, email):
        return (user for user in super().get_users(email) if user.is_verified)
