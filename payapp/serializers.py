from rest_framework import serializers
from .models import CurrencyConversion

class CurrencyConversionSerializer(serializers.Serializer):
    currency_from = serializers.CharField(max_length=3)
    currency_to = serializers.CharField(max_length=3)
    amount_of_currency_from = serializers.DecimalField(max_digits=10, decimal_places=2)