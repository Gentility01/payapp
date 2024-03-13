from register.models import BankAccount
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

class WithdrawForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    bank_account = forms.ModelChoiceField(queryset=None)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bank_account'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Select Bank Account'
        })
        self.fields['amount'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Enter Amount'
        })
        
        # Filter the queryset based on the provided user
        self.fields['bank_account'].queryset = BankAccount.objects.filter(user=user)


class WithdrawConfirmationForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    bank_account = forms.CharField()

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        bank_account = cleaned_data.get('bank_account')

     
        return cleaned_data

    
   

    