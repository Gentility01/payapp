from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from webapps2024.utils.choices import CURRENCY_CHOICES, BankNames
from webapps2024.utils.models import TimeBasedModel
import auto_prefetch
from django_resized import ResizedImageField
from webapps2024.utils.media import MediaHelper
from django.contrib.auth.models import PermissionsMixin
from django.conf import settings

import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, max_length=255)
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return self.username

class User(CustomUser):
    ...

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return self.username

class Administrator(CustomUser, PermissionsMixin):
    objects = CustomUserManager()

    class Meta:
        verbose_name = "Administrator"
        verbose_name_plural = "Administrators"
    

class OnlineAccount(TimeBasedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES.choices)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta(TimeBasedModel.Meta):
        base_manager_name = "prefetch_manager"
        verbose_name_plural = "OnlineAccount"

    def __str__(self):
        return f"Online Account for {self.user.username}"










class UserProfile(TimeBasedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payapp_account = models.CharField(max_length=100, default=uuid.uuid4, editable=False)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = ResizedImageField(
        
        size=[50, 50], quality=100, crop=['middle', 'center'],
        force_format='PNG', upload_to=MediaHelper.get_image_upload_path, blank=True, null=True
    )
    online_account = models.OneToOneField(
        OnlineAccount, on_delete=models.CASCADE, null=True, blank=True
    )
    address = models.CharField(max_length=255, blank=True, null=True)

    class Meta(TimeBasedModel.Meta):
        base_manager_name = "prefetch_manager"
        verbose_name_plural = "User's Profile"


class BankAccount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=50, choices=BankNames, default=BankNames.ACCESS_BANK)
    account_number = models.CharField(max_length=50)
    routing_number = models.CharField(max_length=50)
    

    class Meta:
        verbose_name_plural = "Bank Accounts"

    def __str__(self):
        return f"{self.bank_name}' xxxxxxxxxxx{self.account_number[-4:]}"
    



