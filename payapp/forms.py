from register.models import BankAccount
from .models import Card
from django import forms

class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['bank_name', 'account_number', 'routing_number']
        widgets = {
            'bank_name': forms.Select(attrs={'class': 'form-control'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Number'}),
            'routing_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Routing Number'}),
        }

    def clean_account_number(self):
        account_number = self.cleaned_data['account_number']
        if len(account_number) != 10 or not account_number.isdigit():
            raise forms.ValidationError("Account number must be a 10-digit number.")
        return account_number

    def clean_routing_number(self):
        routing_number = self.cleaned_data['routing_number']
        if len(routing_number) != 10 or not routing_number.isdigit():
            raise forms.ValidationError("Routing number must be a 10-digit number.")
        return routing_number

class WithdrawalForm(forms.Form):
    bank_account = forms.ModelChoiceField(queryset=BankAccount.objects.none(),
                    widget=forms.Select(
                        attrs={'class': 'form-control'})
                    )
    amount = forms.DecimalField(min_value=0.01, 
                    widget=forms.NumberInput(
                        attrs={'class': 'form-control', 'placeholder': 'Enter amount'})
                    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(WithdrawalForm, self).__init__(*args, **kwargs)
        self.fields['bank_account'].queryset = BankAccount.objects.filter(user=user)


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['card_type',  'card_number', 'expiration_date', 'cvv']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'card_type': forms.Select(attrs={'class': 'form-control'}),
            # 'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'card_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Eg. 1234 5678 9012 3456'}),
            # 'expiration_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Expiration Date'}),
            'cvv': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g. 123'}),

        }

    # validates  card number and cvv
    def clean_card_number(self):
        card_number = self.cleaned_data['card_number']
        if len(card_number) != 10 or not card_number.isdigit():
            raise forms.ValidationError("Card number must be a 16-digit number.")
        return card_number
    
    def clean_cvv(self):
        cvv = self.cleaned_data['cvv']
        if len(cvv) != 3 or not cvv.isdigit():
            raise forms.ValidationError("CVV must be a 3-digit number.")
        return cvv


class DirectPaymentForm(forms.Form):
    recipient_email = forms.EmailField(label="Recipient Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    amount = forms.DecimalField(label="Amount", widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))

    