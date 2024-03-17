from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import TemplateView, FormView, DetailView
from register.models import  BankAccount,OnlineAccount, User
from payapp.models import TransactionHistory, Card, CurrencyConversion, Transaction
from payapp.forms import BankAccountForm, WithdrawalForm, CardForm, DirectPaymentForm   
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from decimal import Decimal
from django.db import transaction



# Create your views here.

class HomePageView(TemplateView):
    template_name = "payapp/index.html"

home_page = HomePageView.as_view()



class AccountViews(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('register:login_view')
    template_name = "payapp/account.html"
   
account =  AccountViews.as_view()




class  DashboardView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('register:login_view')
    template_name = "payapp/dashboard.html"

dashboard = DashboardView.as_view()

class Addbank(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('register:login_view')
    model = BankAccount
    form_class = BankAccountForm
    template_name = 'payapp/addbank.html'
    success_url = reverse_lazy('dashboard')  # Redirect to a success URL

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

addbank = Addbank.as_view()

class CardCreateView(CreateView):
    model = Card
    form_class = CardForm
    template_name = 'payapp/create_card.html'
    success_url  =  reverse_lazy('dashboard') 

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

create_card = CardCreateView.as_view()

class WithdrawalView(LoginRequiredMixin, FormView):
    login_url = reverse_lazy('register:login_view')
    template_name = 'payapp/withdraw.html'
    form_class = WithdrawalForm
    success_url = reverse_lazy('withdraw_money_confirm')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    def form_valid(self, form):
        # Store withdrawal details in session variables
        bank_account_id = form.cleaned_data['bank_account'].id
        amount = float(form.cleaned_data['amount'])  # Convert Decimal to float
        self.request.session['withdrawal_details'] = {
            'bank_account_id': bank_account_id,
            'amount': amount,
        }
        return super().form_valid(form)

withdraw = WithdrawalView.as_view()

class ConfirmationView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('register:login_view')
    template_name = 'payapp/withdraw_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        withdrawal_details = self.request.session.get('withdrawal_details')
        if withdrawal_details:
            bank_account_id = withdrawal_details['bank_account_id']
            bank_account = BankAccount.objects.get(pk=bank_account_id)
            form_data = {
                'bank_account': bank_account,
                'amount': withdrawal_details['amount'],
            }
            # Create the form instance
            form = WithdrawalForm(user=self.request.user, initial=form_data)
            # Disable all form fields
            for field in form.fields.values():
                field.widget.attrs['disabled'] = True
            context['form'] = form
        else:
            messages.error(self.request, 'Withdrawal details not found')
        return context

    def post(self, request, *args, **kwargs):
        form = WithdrawalForm(request.POST, user=request.user)
        if form.is_valid():
            bank_account = form.cleaned_data['bank_account']
            amount = form.cleaned_data['amount']
            online_account = OnlineAccount.objects.get(user=request.user)
            if online_account.balance >= amount:
                online_account.balance -= amount
                online_account.save()

                # Record the transaction history
                TransactionHistory.objects.create(
                    sender=request.user, description='Withdrawal to bank account',
                     status='✔️', amount=amount, bank_account=bank_account)

                del request.session['withdrawal_details']
                messages.success(request, 'Withdrawal successful')
                return redirect('withdraw_success')
            else:
                messages.error(request, 'Insufficient balance')
        return self.render_to_response(self.get_context_data(request=request, form=form))

withdraw_money_confirm = ConfirmationView.as_view()

class SuccessView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('register:login_view')
    template_name = 'payapp/withdrawal_success.html'



class DepositeView(LoginRequiredMixin, TemplateView):
    template_name = 'payapp/deposite.html'
    login_url = reverse_lazy('register:login_view')

    def post(self, request, *args, **kwargs):
        # process the form submission
        payment_method = request.POST.get("payment_method")
        amount = request.POST.get('amount')

        if payment_method == "Bank Accounts":
            return redirect( reverse("bank_selection") + f"?amount={amount}")
        elif payment_method == "Credit or Debit Cards":
            return redirect( reverse("card_selection") + f"?amount={amount}")
        else:
            # Redirect back to deposit form if invalid selection
            return redirect(reverse('deposite'))

deposite = DepositeView.as_view()

class BankSelectionView(TemplateView):
    template_name = "payapp/bank_selection.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['amount'] = self.request.GET.get('amount', '')
        context['bank_accounts'] = BankAccount.objects.filter(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        bank_account_id = request.POST.get("bank_account")
        amount = Decimal(request.POST.get("amount"))  # Convert amount to Decimal
        bank_account = get_object_or_404(BankAccount, id=bank_account_id, user=request.user)

        # Update user's online account balance
        online_account = OnlineAccount.objects.get(user=request.user)
        online_account.balance += amount  # Add amount directly (now it's a Decimal)
        online_account.save()

        # Record transaction history
        TransactionHistory.objects.create(
            sender=request.user,
            description='Deposit from bank account',
            status='✔️',
            amount=amount,
            bank_account=bank_account
        )

        # Convert bank_account_id to integer
        bank_account_id = int(bank_account_id)

        return redirect(reverse('bank_deposit_receipt', kwargs={'pk': bank_account_id}) + f'?amount={amount}')

bank_selection = BankSelectionView.as_view()


class BankDepositReceiptView(DetailView):
    model = BankAccount
    template_name = 'payapp/bank_deposit_receipt.html'
    context_object_name = 'bank_account'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['amount'] = self.request.GET.get('amount', '')
        return context
    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)

bank_deposit_receipt = BankDepositReceiptView.as_view()


class CardSelectionView(TemplateView):
    template_name = "payapp/card_selection.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['amount'] = self.request.GET.get('amount', '')
        context['cards'] = Card.objects.filter(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        card_id = request.POST.get("card")
        amount = Decimal(request.POST.get("amount"))  # Convert amount to Decimal
        card = get_object_or_404(Card, id=card_id, user=request.user)

        # Update user's online account balance
        online_account = OnlineAccount.objects.get(user=request.user)
        online_account.balance += amount  # Add amount directly (now it's a Decimal)
        online_account.save()

        # Record transaction history
        TransactionHistory.objects.create(
            sender=request.user,
            description='Deposit from card',
            status='✔️',
            amount=amount,)
        
        return redirect(reverse('card_deposit_receipt', kwargs={'pk': card_id}) + f'?amount={amount}')

card_selection = CardSelectionView.as_view()

class CardDepositReceiptView(DetailView):
    model = Card
    template_name = 'payapp/card_deposit_receipt.html'
    context_object_name = 'card'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['amount'] = self.request.GET.get('amount', '')
        return context

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)

card_deposit_receipt = CardDepositReceiptView.as_view()

class DirectPaymentViews(FormView):
    template_name = "payapp/direct_payment.html"
    form_class = DirectPaymentForm
    success_url = reverse_lazy('payment_success')

    def form_valid(self, form):
        sender = self.request.user
        recipient_email = form.cleaned_data['recipient_email']
        amount = form.cleaned_data['amount']

        recipient = get_object_or_404(User, email=recipient_email)
        
        # Check if the sender has enough funds in their account
        sender_account = sender.onlineaccount
        if sender_account.balance < amount:
            # Sender doesn't have enough funds
            messages.error(self.request, "Insufficient funds.")
            return self.form_invalid(form)
        
        # Perform currency conversion if necessary
        if sender_account.currency != recipient.onlineaccount.currency:
            conversion_rate = get_object_or_404(CurrencyConversion, currency_from=sender_account.currency, currency_to=recipient.onlineaccount.currency)
            converted_amount = amount * conversion_rate.exchange_rate
        else:
            converted_amount = amount
        
        # Deduct the amount from the sender's account and add it to the recipient's account within a single transaction
        with transaction.atomic():
            sender_account.balance -= amount
            sender_account.save()
            recipient_account = recipient.onlineaccount
            recipient_account.balance += converted_amount
            recipient_account.save()
            
            # Create a transaction record for the payment
            Transaction.objects.create(sender=sender, recipient=recipient, amount=amount, transaction_type="direct_payment")
            
            # Create a transaction history record for the payment
            TransactionHistory.objects.create(sender=sender, recipient=recipient, status="✔️", amount=amount, description="Direct payment")
        messages.success(self.request, "Payment successful.")
        return super().form_valid(form)

direct_payment_view = DirectPaymentViews.as_view()

