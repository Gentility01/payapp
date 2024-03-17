from django.db import models
from django.contrib.auth.models import AbstractUser
from webapps2024.utils.choices import CURRENCY_CHOICES, BankNames
from webapps2024.utils.models import TimeBasedModel
import auto_prefetch
from django_resized import ResizedImageField
from webapps2024.utils.media import MediaHelper
import uuid


class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=255, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:
        return self.username
    

class OnlineAccount(TimeBasedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES.choices)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000)

    class Meta(TimeBasedModel.Meta):
        base_manager_name = "prefetch_manager"
        verbose_name_plural = "OnlineAccount"

    def __str__(self):
        return f"Online Account for {self.user.username}"



class Adminstrator(TimeBasedModel):
    user = auto_prefetch.OneToOneField(User, on_delete=models.CASCADE, related_name="administrator", null=True, blank=True)

    class Meta(TimeBasedModel.Meta):
        base_manager_name = "prefetch_manager"
        verbose_name_plural = "Admins"

class UserProfile(TimeBasedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    payapp_account = models.CharField(max_length=100, default=uuid.uuid4, editable=False)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = ResizedImageField(
        default="images/default.png", 
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=50, choices=BankNames, default=BankNames.ACCESS_BANK)
    account_number = models.CharField(max_length=50)
    routing_number = models.CharField(max_length=50)
    

    class Meta:
        verbose_name_plural = "Bank Accounts"

    def __str__(self):
        return f"{self.bank_name}' xxxxxxxxxxx{self.account_number[-4:]}"
    



