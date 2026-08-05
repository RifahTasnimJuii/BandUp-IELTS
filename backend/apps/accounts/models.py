from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, Group, Permission, PermissionsMixin
from django.db import models

from apps.common.models import TimeStampedModel, UUIDModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field is required.')
        if not username:
            raise ValueError('The Username field is required.')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.SUPERADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email=email, username=username, password=password, **extra_fields)


class User(UUIDModel, TimeStampedModel, AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        CONTENT_EDITOR = 'content_editor', 'Content Editor'
        ADMIN = 'admin', 'Admin'
        SUPERADMIN = 'superadmin', 'Superadmin'

    class AuthProvider(models.TextChoices):
        EMAIL = 'email', 'Email'
        GOOGLE = 'google', 'Google'

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.STUDENT)
    auth_provider = models.CharField(max_length=32, choices=AuthProvider.choices, default=AuthProvider.EMAIL)
    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='accounts_user_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='accounts_user_permissions',
        related_query_name='user',
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Profile(UUIDModel, TimeStampedModel):
    class LanguagePreference(models.TextChoices):
        EN = 'en', 'English'
        BN = 'bn', 'Bengali'

    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='profile')
    target_band = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    country = models.CharField(max_length=128, null=True, blank=True)
    language_preference = models.CharField(max_length=2, choices=LanguagePreference.choices, default=LanguagePreference.EN)
    timezone = models.CharField(max_length=64, default='UTC')
    dark_mode = models.BooleanField(default=False)
    leaderboard_opt_in = models.BooleanField(default=False)
    exam_instructions_acknowledged = models.BooleanField(default=False)
    streak_count = models.IntegerField(default=0)
    last_practice_at = models.DateTimeField(null=True, blank=True)
    avatar_url = models.URLField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    speaking_audio_consent = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.email} Profile'
