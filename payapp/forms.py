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




    
   

    