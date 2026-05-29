from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from .avatar import generate_avatar_image


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        if not user.avatar:
            user.avatar.save(
                f"avatar_{email}.png",
                generate_avatar_image(user.name or "U"),
                save=False,
            )
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("name", "Admin")
        extra_fields.setdefault("surname", "User")
        extra_fields.setdefault("phone", "+70000000000")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to="avatars/")
    phone = models.CharField(max_length=12)
    github_url = models.URLField(blank=True)
    about = models.TextField(blank=True, max_length=256)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname", "phone"]

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar.save(
                f"avatar_{self.email or 'user'}.png",
                generate_avatar_image(self.name or "U"),
                save=False,
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
