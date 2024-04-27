# exchange_rates.py
# from payapp.models import CurrencyConversion
# from decimal import Decimal, InvalidOperation

MANUAL_EXCHANGE_RATES = {
    ("USD", "USD"): 1,
    ("USD", "EUR"): 0.93335,
    ("USD", "GBP"): 0.79991,
    ("EUR", "USD"): 1.07126,
    ("EUR", "GBP"): 0.85697,
    ("EUR", "JPY"): 168.099,
    ("GBP", "USD"): 1.24994,
    ("GBP", "EUR"): 1.16669,
}