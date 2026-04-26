import re

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models

PHONE_LENGTH_RU_STANDARD = 11
PHONE_LENGTH_RU_WITH_PLUS = 12
PHONE_PREFIX_8 = "8"
PHONE_PREFIX_7 = "7"
PHONE_PREFIX_PLUS = "+"
PHONE_PREFIXES_RU = (PHONE_PREFIX_8, PHONE_PREFIX_7)

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль", widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Придумайте пароль"})
    )

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Имя"}),
            "surname": forms.TextInput(attrs={"class": "form-control", "placeholder": "Фамилия"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Введите email"})
    )
    password = forms.CharField(
        label="Пароль", widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Введите пароль"})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError("Неверный имейл или пароль")
            cleaned_data["user"] = user
        return cleaned_data


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "surname": forms.TextInput(attrs={"class": "form-control"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
            "about": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "89991234567 или +79991234567"}),
            "github_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://github.com/username"}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        if phone is None:
            phone = ""
        phone = phone.strip()

        if not phone:
            return None

        normalized = re.sub(r"[^\d]", "", phone)
        is_valid_format = (
            len(normalized) == PHONE_LENGTH_RU_STANDARD and normalized.startswith(PHONE_PREFIXES_RU)
        ) or (
            len(normalized) == PHONE_LENGTH_RU_WITH_PLUS
            and normalized.startswith(PHONE_PREFIX_7)
            and phone.startswith(PHONE_PREFIX_PLUS)
        )

        if not is_valid_format:
            raise forms.ValidationError("Неверный формат телефона. Допустимы: 8XXXXXXXXXX или +7XXXXXXXXXX")

        if normalized.startswith(PHONE_PREFIX_8):
            normalized_db = PHONE_PREFIX_7 + normalized[1:]
        else:
            normalized_db = normalized.lstrip(PHONE_PREFIX_PLUS)

        existing = User.objects.filter(
            models.Q(phone=normalized_db)
            | models.Q(phone=PHONE_PREFIX_PLUS + normalized_db)
            | models.Q(phone=PHONE_PREFIX_8 + normalized_db[1:])
        )
        if self.instance and self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise forms.ValidationError("Этот номер телефона уже используется другим пользователем.")

        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        if url:
            if not url.startswith(("https://github.com/", "http://github.com/")):
                raise forms.ValidationError("Ссылка должна вести на GitHub.")
            try:
                URLValidator()(url)
            except ValidationError:
                raise forms.ValidationError("Некорректная ссылка.")
        return url


PasswordChangeForm = DjangoPasswordChangeForm
