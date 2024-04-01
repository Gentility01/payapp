from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class CURRENCY_CHOICES(TextChoices):
    US_DOLLAR = ("USD", _("🇺🇸 US Dollars"))
    EUROS = ("EUR", _("🇪🇺 Euros"))
    POUND = ("GBP", _("🇬🇧 Pounds"))
    # YEN = ("JPY", _("🇯🇵 Yen"))
    # CHINESES_YEN = ("CNY", _("🇨🇳 Chinese Yuan"))
    # RUPEE = ("INR", _("🇮🇳 Rupee"))
    # CANADIAN_DOLLAR = ("CAD", _("🇨🇦 Canadian Dollars"))
    # BITCOIN = ("BTC", _("🔒 Bitcoin"))
    # ETHEREUM = ("ETH", _("🧬 Ethereum"))
    # NAIRA = ("NGN", _("🇳🇬 Nigerian Naira"))


class TRASACTION_TYPE_CHOICES(TextChoices):
    DEPOSITE = ("DEPOSIT", "Deposit")
    WITHDRAWAL = ("WITHDRAWAL", "Withdrawal")
    TRANSFER = ("TRANSFER", "Transfer")
    CONVERSION = ("CONVERSION", "Conversion")
    REQUEST = ("REQUEST", "Request")


class BankNames(TextChoices):
    BANK_OF_AMERICA = ("BANK_OF_AMERICA", "Bank of America")
    CHINA_UNION_PAY = ("CHINA_UNION_PAY", "China Union Pay")
    CREDIT_AGRICOLE = ("CREDIT_AGRICOLE", "Credit Agricole")
    CREDIT_SUISSE = ("CREDIT_SUISSE", "Credit Suisse")
    DEUTSCHE_BANK = ("DEUTSCHE_BANK", "Deutsche Bank")
    JPMORGAN_CHASE = ("JPMORGAN_CHASE", "JPMorgan Chase")
    MASTERCARD = ("MASTERCARD", "Mastercard")
    ACCESS_BANK = ("ACCESS_BANK", "Access Bank")
    FIRST_BANK = ("FIRST_BANK", "First Bank of Nigeria")
    GTBANK = ("GTBANK", "Guaranty Trust Bank")
    ZENITH_BANK = ("ZENITH_BANK", "Zenith Bank")
    UBA = ("UBA", "United Bank for Africa")
    STANBIC_IBTC = ("STANBIC_IBTC", "Stanbic IBTC Bank")


class CARD_TYPE(TextChoices):
    DEPOSITE = ("DEPOSITE", "Deposite")
    CREDIT = ("CREDIT", "Credit")


class TRANSACTION_STATUS(TextChoices):
    PENDING = ("PENDING", "Pending")
    SUCCESS = ("SUCCESS", "Success")
    FAILED = ("FAILED", "Failed")

