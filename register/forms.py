from django import forms  
from django.contrib.auth.forms import UserCreationForm
from .models import User, OnlineAccount
from  webapps2024.utils.choices import CURRENCY_CHOICES


class RegistrationForm(UserCreationForm):
    full_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data["full_name"]
        first_name, last_name = full_name.split(" ", 1)
        user.first_name = first_name
        user.last_name = last_name
        if commit:
            user.save()
        return user
    
    # adding widgets
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['full_name'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Enter First and Last Name'
        })
        self.fields['username'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Enter your username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Enter your email'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Enter your password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Confirm your password'
        })

        
class OnlineAccountForm(forms.ModelForm):
    class Meta:
        model = OnlineAccount
        fields = ['currency']
        widgets = {
            'currency': forms.Select(attrs={'class': 'form-select', 'required': 'required'}, choices=CURRENCY_CHOICES),
        }


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Enter your email'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Enter your password'
        })