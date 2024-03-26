import auto_prefetch
from django.db import models
from webapps2024.utils.models import TimeBasedModel
from webapps2024.utils.choices import CURRENCY_CHOICES, TRASACTION_TYPE_CHOICES, CARD_TYPE, TRANSACTION_STATUS
from register.models import User
from django.conf import settings
# Create your models here.

class Transaction(TimeBasedModel):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_transactions')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type  = models.CharField(max_length=11, choices=TRASACTION_TYPE_CHOICES)
    status = models.CharField(max_length=11, choices=TRANSACTION_STATUS, blank=True, null=True)
    class Meta(TimeBasedModel.Meta):
        base_manager_name = "prefetch_manager"
        verbose_name_plural = "transactions"


    # def perform_transaction(self):
    #     """
    #     Perform the transaction and handle currency conversion if necessary.
    #     """
    #     if self.sender.onlineaccount.currency != self.recipient.onlineaccount.currency:
    #         # Currency conversion needed
    #         conversion_rate = CurrencyConversion.objects.get(currency_from=self.sender.onlineaccount.currency, currency_to=self.recipient.onlineaccount.currency)
    #         converted_amount = conversion_rate.convert_currency(self.amount)
    #         self.amount = converted_amount
    #         self.currency = self.recipient.onlineaccount.currency
        
    #     # Update sender's and receiver's account balances
    #     self.sender.onlineaccount.balance -= self.amount
    #     self.recipient.onlineaccount.balance += self.amount
    #     self.sender.onlineaccount.save()
    #     self.recipient.onlineaccount.save()
        
    #     # Mark the transaction as completed
    #     self.status = 'completed'
    #     self.save()

    def __str__(self):
        return f"{self.sender.username} sent {self.amount} {self.currency} to {self.recipient.username}"
    




class CurrencyConversion(models.Model):
    currency_from = models.CharField(max_length=10, choices=CURRENCY_CHOICES.choices)
    currency_to = models.CharField(max_length=10, choices=CURRENCY_CHOICES.choices)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=6)

    def convert_currency(self, transaction):
        """
        Convert the given amount from currency_from to currency_to based on the exchange rate.
        """
        converted_amount = transaction.amount * self.exchange_rate
        return round(converted_amount, 2)

    def __str__(self):
        return f"{self.currency_from}/{self.currency_to}: {self.exchange_rate}"




class TransactionHistory(TimeBasedModel):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_transaction_histories', blank=True, null=True)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_transaction_histories', blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bank_account = models.ForeignKey('register.BankAccount', on_delete=models.CASCADE, blank=True, null=True)

    class Meta(TimeBasedModel.Meta):
        base_manager_name = "prefetch_manager"
        verbose_name_plural = "Transaction histories"
    

    def __str__(self):
        return f'{self.created_at} - {self.description} - {self.amount}'

    def accept_request(self):
        self.status = 'Accepted'
        self.save()

    def reject_request(self):
        self.status = 'Rejected'
        self.save()

    def generate_notification(self):
        recipient = self.recipient
        message = f"You have received a payment request from {self.sender.username}. Amount: {self.amount}."
        # Assuming you have a method to handle sending notifications to users
        self.send_notification(recipient, message)


class Card(TimeBasedModel):
    user  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    card_type = models.CharField(max_length=20, choices=CARD_TYPE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)
    card_number = models.CharField(max_length=10, blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    cvv = models.CharField(max_length=4, blank=True, null=True)


class PaymentRequest(TimeBasedModel):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_payment_requests')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_payment_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField()
    status = models.CharField(max_length=11, choices=TRANSACTION_STATUS, blank=True, null=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES.choices, blank=True, null=True)



