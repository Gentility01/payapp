# Generated by Django 5.0.3 on 2024-03-12 09:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("register", "0002_alter_onlineaccount_currency_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="userprofile",
            old_name="paypal_account",
            new_name="payapp_account",
        ),
    ]
