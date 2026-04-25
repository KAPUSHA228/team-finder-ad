from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Название проекта"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 5, "placeholder": "Опишите суть проекта"}
            ),
            "github_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://github.com/..."}),
            "status": forms.Select(attrs={"class": "form-control"}),
        }

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        if url:
            if not url.startswith(("https://github.com/", "http://github.com/")):
                raise forms.ValidationError("Ссылка должна вести на GitHub.")
            try:
                URLValidator()(url)
            except ValidationError:
                raise forms.ValidationError("Некорректный URL.")
        return url
