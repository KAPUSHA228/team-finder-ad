import io
import random

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont


class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, name, surname, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("email address", unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    phone = models.CharField(max_length=12, unique=True, null=True, blank=True)
    github_url = models.URLField(blank=True)
    about = models.TextField(max_length=256, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    def save(self, *args, **kwargs):
        if self.phone == "":
            self.phone = None
        if not self.avatar and self.name:
            self._generate_avatar()
        super().save(*args, **kwargs)

    def _generate_avatar(self):
        img = Image.new("RGB", (200, 200), color=self._get_random_color())
        draw = ImageDraw.Draw(img)

        letter = self.name[0].upper() if self.name else "?"

        try:
            font = ImageFont.truetype("arial.ttf", 100)
        except OSError:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((200 - text_width) // 2, (200 - text_height) // 2)

        draw.text(position, letter, fill="white", font=font)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        filename = f'avatar_{self.pk or "new"}.png'
        self.avatar.save(filename, ContentFile(buffer.read()), save=False)

    def _get_random_color(self):
        colors = [
            (100, 149, 237),
            (144, 238, 144),
            (255, 182, 193),
            (221, 160, 221),
            (173, 216, 230),
            (255, 218, 185),
            (176, 224, 230),
            (240, 230, 140),
            (255, 160, 122),
        ]
        return random.choice(colors)

    def __str__(self):
        return f"{self.surname} {self.name}"
