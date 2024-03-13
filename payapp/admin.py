from django.contrib import admin
from .models import Transaction, CurrencyConversion
# Register your models here.

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'amount', 'get_currency', 'transaction_type']
    search_fields = ['sender__username', 'recipient__username']
    list_filter = ['transaction_type']

    def get_currency(self, obj):
        return obj.currency
    get_currency.short_description = 'Currency'
@admin.register(CurrencyConversion)
class CurrencyConversionAdmin(admin.ModelAdmin):
    list_display = ['currency_from', 'currency_to', 'exchange_rate']