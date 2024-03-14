import auto_prefetch
from django.db import models
from webapps2024.utils.models import TimeBasedModel
from webapps2024.utils.choices import CURRENCY_CHOICES, TRASACTION_TYPE_CHOICES
from register.models import User
# Create your models here.

class Transaction(TimeBasedModel):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_transactions")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type  = models.CharField(max_length=11, choices=TRASACTION_TYPE_CHOICES)

    class Meta(TimeBasedModel.Meta):
        base_manager_name = "prefetch_manager"
        verbose_name_plural = "transactions"


    def perform_transaction(self):
        """
        Perform the transaction and handle currency conversion if necessary.
        """
        if self.sender.onlineaccount.currency != self.recipient.onlineaccount.currency:
            # Currency conversion needed
            conversion_rate = CurrencyConversion.objects.get(currency_from=self.sender.onlineaccount.currency, currency_to=self.recipient.onlineaccount.currency)
            converted_amount = conversion_rate.convert_currency(self.amount)
            self.amount = converted_amount
            self.currency = self.recipient.onlineaccount.currency
        
        # Update sender's and receiver's account balances
        self.sender.onlineaccount.balance -= self.amount
        self.recipient.onlineaccount.balance += self.amount
        self.sender.onlineaccount.save()
        self.recipient.onlineaccount.save()
        
        # Save the transaction
        self.save()

    def __str__(self):
        return f"{self.sender.username} sent {self.amount} {self.currency} to {self.recipient.username}"




class CurrencyConversion(models.Model):
    currency_from = models.CharField(max_length=3)
    currency_to = models.CharField(max_length=3)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=6)

    def convert_currency(self, amount):
        """
        Convert the given amount from currency_from to currency_to based on the exchange rate.
        """
        converted_amount = amount * self.exchange_rate
        return round(converted_amount, 2)

    def __str__(self):
        return f"{self.currency_from}/{self.currency_to}: {self.exchange_rate}"




class TransactionHistory(TimeBasedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f'{self.created_at} - {self.description} - {self.amount}'
