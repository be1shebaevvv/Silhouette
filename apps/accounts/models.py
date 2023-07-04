from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager



class UserManager(BaseUserManager):

    def create_user(self, username=None, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is must be set")
        email = self.normalize_email(email)
        username = self.model(username=username, **extra_fields)
        username.set_password(password)
        # "qwerty123!" --> askdjflkjfj3i501irkferjflkjsf --> "qwerty123!"
        username.save()
        return username
    

    def create_superuser(self, username, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(username, password, **extra_fields)

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField("Никнейм", max_length=150, unique=True)
    email = models.EmailField("Электронная почта", unique=True)
    image = models.ImageField("Аватарка", upload_to="media/users/profiles_images/", blank=True, null=True)
    date_of_birth = models.DateField("Дата рождения", blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    followers = models.ManyToManyField("self", related_name='following', symmetrical=False)
    subscriptions = models.ManyToManyField("self", related_name='subscribers', symmetrical=False)
    login = models.DateTimeField(null=True, blank=True)
    GENDER_CHOICES = (
        ('Мужской', 'Мужской'),
        ('Женский', 'Женский'),
        ('Неизвестный','Неизвестный')
    )
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='Неизвестный')


    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
    
    def __str__(self):
        return self.username
