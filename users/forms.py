import hashlib
import re

from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from .models import User

PHONE_PATTERN = re.compile(r"^(8\d{10}|\+7\d{10})$")


def normalize_phone(phone: str) -> str:
    if phone.startswith("8"):
        return "+7" + phone[1:]
    return phone


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("name", "surname", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        email = user.email
        digits = hashlib.md5(email.encode()).hexdigest()[:10]
        user.phone = f"+7{digits}"
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            self.user = authenticate(username=email, password=password)
            if self.user is None:
                raise ValidationError("Неверный email или пароль")

        return cleaned_data


class UserEditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone or not PHONE_PATTERN.match(phone):
            raise ValidationError("Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX")

        normalized = normalize_phone(phone)
        alternate = "8" + normalized[2:] if normalized.startswith("+7") else normalized

        qs = User.objects.filter(phone__in=[normalized, alternate])
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Пользователь с таким номером телефона уже существует")

        return normalized

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url")
        if github_url and "github.com" not in github_url:
            raise ValidationError("Ссылка должна вести на github.com")
        return github_url


class UserChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password1 = forms.CharField(widget=forms.PasswordInput)
    new_password2 = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):
            raise ValidationError("Old password is incorrect")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError("New passwords do not match")

        return cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data["new_password1"])
        self.user.save()
