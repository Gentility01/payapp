from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import TransactionHistory

@receiver(post_save, sender=TransactionHistory)
def send_notification(sender, instance, created, **kwargs):
    if created:
        recipient_email = instance.recipient.email
        sender_name = instance.sender.username
        subject = "New Payment Request"
        message = f"Dear {instance.recipient.username},\n\nYou have received a new payment request from {sender_name}.\n\nAmount: {instance.amount}\nDescription: {instance.description}\n\nPlease log in to your account to review and respond to the request.\n\nRegards,\nYour Application Team"
        send_mail(subject, message, None, [recipient_email])
