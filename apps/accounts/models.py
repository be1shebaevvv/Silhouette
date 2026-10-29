from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    """Manager that creates users with normalized email addresses."""

    use_in_migrations = True

    def create_user(self, username=None, password=None, **extra_fields):
        if not username:
            raise ValueError("A username must be provided.")

        email = self.normalize_email(extra_fields.get("email", ""))
        extra_fields["email"] = email
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField("Никнейм", max_length=150, unique=True)
    email = models.EmailField("Электронная почта", unique=True)
    image = models.ImageField(
        "Аватарка",
        upload_to="media/users/profiles_images/",
        blank=True,
        null=True,
    )
    date_of_birth = models.DateField("Дата рождения", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Existing accounts stay verified; registration explicitly sets this to False.
    is_verified = models.BooleanField(default=True)
    followers = models.ManyToManyField("self", related_name="following", symmetrical=False)
    subscriptions = models.ManyToManyField("self", related_name="subscribers", symmetrical=False)
    login = models.DateTimeField(null=True, blank=True)

    GENDER_CHOICES = (
        ("Мужской", "Мужской"),
        ("Женский", "Женский"),
        ("Неизвестный", "Неизвестный"),
    )
    gender = models.CharField(
        "Пол",
        max_length=20,
        choices=GENDER_CHOICES,
        default="Неизвестный",
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
