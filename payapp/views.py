import json
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import TemplateView, FormView, DetailView, ListView, RedirectView, UpdateView
from register.models import  BankAccount,OnlineAccount, User
from payapp.models import TransactionHistory, Card, CurrencyConversion, Transaction, PaymentRequest
from payapp.forms import BankAccountForm, WithdrawalForm, CardForm, DirectPaymentForm, PaymentRequestForm
from django.core.serializers.json import DjangoJSONEncoder 
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from decimal import Decimal
from django.db import transaction
from webapps2024.utils.manual_exchange_rate import MANUAL_EXCHANGE_RATES

from django.contrib import messages



# Create your views here.

class HomePageView(TemplateView):
    template_name = "payapp/index.html"

home_page = HomePageView.as_view()



class AccountViews(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('register:login_view')
    template_name = "payapp/account.html"
   
account =  AccountViews.as_view()


# ---------------------------------------------------------------- Dashboard -------------------------------------------------------------------

class  DashboardView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('register:login_view')
    template_name = "payapp/dashboard.html"

dashboard = DashboardView.as_view()


# ------------------------------------------------------------------Add Bank ------------------------------------------------------------------------
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

# ------------------------------------------------------------------Add Credit card ------------------------------------------------------------------------
class CardCreateView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('register:login_view')
    model = Card
    form_class = CardForm
    template_name = 'payapp/create_card.html'
    success_url  =  reverse_lazy('dashboard') 

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

create_card = CardCreateView.as_view()

# ------------------------------------------------------------------Withdraw money ------------------------------------------------------------------------
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


# ------------------------------------------------------------------Confirm Widthdrawal  view / widthdraw details ------------------------------------------------------------------------
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

# ------------------------------------------------------------------Widthdraw success ------------------------------------------------------------------------
class SuccessView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('register:login_view')
    template_name = 'payapp/withdrawal_success.html'



# ------------------------------------------------------------------Deposit money view  ------------------------------------------------------------------------
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


# ------------------------------------------------------------------Bank Selection for withdrawal  ------------------------------------------------------------------------
class BankSelectionView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('register:login_view')
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


# ------------------------------------------------------------------Bank Deposit Receipt  ------------------------------------------------------------------------
class BankDepositReceiptView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy('register:login_view')
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



# ------------------------------------------------------------------Select card for withdrawal ------------------------------------------------------------------------
class CardSelectionView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('register:login_view')
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

# ------------------------------------------------------------------ Card Deposit Receipt ------------------------------------------------------------------------
class CardDepositReceiptView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy('register:login_view')
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


# ------------------------------------------------------------------Direct Payment or Send money ------------------------------------------------------------------------
class DirectPaymentFormView(LoginRequiredMixin, FormView):
    login_url = reverse_lazy('register:login_view')
    template_name = "payapp/direct_payment_form.html"
    form_class = DirectPaymentForm
    success_url = reverse_lazy('payment_confirmation')

    def form_valid(self, form):
        # Store form data in session for display on the next page
        payment_data = form.cleaned_data
        # Convert Decimal objects to strings
        payment_data['amount'] = str(payment_data['amount'])
        self.request.session['payment_data'] = payment_data  # Store payment data directly
        return redirect('payment_confirmation')

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


# ------------------------------------------------------------------Direct or send money confirmation ------------------------------------------------------------------------
class DirectPaymentConfirmationView(LoginRequiredMixin, FormView):
    template_name = "payapp/direct_payment_confirmation.html"
    form_class = DirectPaymentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment_data = self.request.session.get('payment_data', {})
        recipient_email = payment_data.get('recipient_email')

        try:
            # Get the recipient user by email
            recipient = User.objects.get(email=recipient_email)
            context['recipient'] = recipient
        except User.DoesNotExist:
            context['recipient_not_found'] = True  # Set flag indicating recipient not found
            context['error_message'] = "Recipient user not found."
        
        context['payment_data'] = payment_data
        return context

    def form_valid(self, form):
        payment_data = self.request.session.get('payment_data', {})
        sender = self.request.user
        recipient_email = payment_data.get('recipient_email')
        amount = payment_data.get('amount')

        # Check if the recipient email is the same as the sender's email
        if sender.email == recipient_email:
            messages.error(self.request, "You cannot send a payment request to yourself.")
            return redirect('payment_failed')

        try:
            # Try to get the recipient user by email
            recipient = User.objects.get(email=recipient_email)
        except User.DoesNotExist:
            messages.error(self.request, "Recipient user not found.")
            return redirect('payment_failed')

        # Check if the sender has enough funds in their account
        sender_account = sender.onlineaccount
        if sender_account.balance < float(amount):
            # Sender doesn't have enough funds
            messages.error(self.request, "Insufficient funds.")
            return redirect('payment_failed')
        
        # Deduct the amount from the sender's account and add it to the recipient's account within a single transaction
        with transaction.atomic():
            sender_account.balance -= int(amount)
            sender_account.save()
            recipient_account = recipient.onlineaccount
            recipient_account.balance += int(amount)  # No currency conversion needed
            recipient_account.save()
            
            # Create a transaction record for the payment
            Transaction.objects.create(sender=sender, recipient=recipient, amount=amount, transaction_type="direct_payment")
            
            # Create transaction history records for both sender and recipient
            TransactionHistory.objects.create(sender=sender, recipient=recipient, status="✔️", amount=amount, description="Direct payment (sent)")
            TransactionHistory.objects.create(sender=recipient, recipient=sender, status="📥", amount=amount, description="Direct payment (received)")
        
        # Clear session data
        self.request.session.pop('payment_data', None)

        return redirect('payment_success')


# ------------------------------------------------------------------Successful Payment Trasaction ------------------------------------------------------------------------
class PaymentSuccess( LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('register:login_view')
    template_name = "payapp/payment_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment_data'] = self.request.session.get('payment_data', {})
        return context

# ------------------------------------------------------------------Payment Transanction Fialed  ------------------------------------------------------------------------
class PaymentFailed(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('register:login_view')
    template_name = "payapp/payment_failed.html"


payment_failed = PaymentFailed.as_view()
payment_success_view = PaymentSuccess.as_view()
direct_payment_view = DirectPaymentFormView.as_view()
direct_payment_confirmation_view = DirectPaymentConfirmationView.as_view()


# ------------------------------------------------------------------Request Payment ------------------------------------------------------------------------
class CreatePaymentRequestView(CreateView):
    model = PaymentRequest
    form_class = PaymentRequestForm
    template_name = 'payapp/request_payment.html'
    success_url = reverse_lazy('payment_request_success')

    def form_valid(self, form):
        recipient_email = form.cleaned_data['recipient_email']
        # recipient = User.objects.get(email=recipient_email)
        # Check if the recipient exists
        try:
            recipient = User.objects.get(email=recipient_email)
        except User.DoesNotExist:
            messages.error(self.request, 'Recipient user not found!')
            return redirect('payment_failed')
        # Check if the recipient's email is the same as the sender's email
        if recipient == self.request.user:
            messages.error(self.request, 'You cannot send a payment request to yourself!')
            return redirect('payment_failed')
         
        
        form.instance.sender = self.request.user
        form.instance.recipient = recipient
        form.instance.status = 'pending'
        
        # Create transaction history records for both sender and recipient
        sender = self.request.user
        amount = form.cleaned_data['amount']
        TransactionHistory.objects.create(sender=sender, recipient=recipient, status="✔️", amount=amount, description="Request Payment (sent)")
        TransactionHistory.objects.create(sender=recipient, recipient=sender, status="📥", amount=amount, description="Request Payment (received)")

        messages.success(self.request, 'Payment request sent successfully!')
        return super().form_valid(form)

request_payment_view = CreatePaymentRequestView.as_view()

# -----------------------------------------------------------------------------------Payment Request successful ------------------------------------------------------------------------
class PaymentRequestSuccess(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('register:login_view')
    template_name = 'payapp/payment_request_success.html'

payment_request_success = PaymentRequestSuccess.as_view()


# ------------------------------------------------------------------------------------Payment Request List------------------------------------------------------------------------
class PaymentRequestListView(LoginRequiredMixin, ListView):
    model = PaymentRequest
    template_name = 'payapp/payment_request_list.html'
    context_object_name = 'payment_requests'

    def get_queryset(self):
        return PaymentRequest.objects.filter(recipient=self.request.user).order_by('-created_at')

payment_request_list = PaymentRequestListView.as_view()


# ------------------------------------------------------------------------------------Respond to Payment Request------------------------------------------------------------------------
class RespondToPaymentRequestView(UpdateView):
    model = PaymentRequest
    fields = ['status']
    template_name = 'respond_to_payment_request.html'
    success_url = reverse_lazy('payment_request_list')

    def form_valid(self, form):
        payment_request = form.instance
        sender_account = OnlineAccount.objects.get(user=payment_request.sender)
        recipient_account = OnlineAccount.objects.get(user=payment_request.recipient)

        if payment_request.status == 'accepted':
            if sender_account.balance >= payment_request.amount:
                sender_account.balance -= payment_request.amount
                recipient_account.balance += payment_request.amount
                sender_account.save()
                recipient_account.save()
                messages.success(self.request, 'Payment request accepted!')
            else:
                messages.error(self.request, 'Insufficient balance to fulfill the payment request.')
                return redirect('payment_failed')
        elif payment_request.status == 'rejected':
            messages.info(self.request, 'Payment request rejected!')
        
        return super().form_valid(form)

    def get_queryset(self):
        return PaymentRequest.objects.filter(recipient=self.request.user)


# ------------------------------------------------------------------------------------Transaction List------------------------------------------------------------------------
class TransactionList(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'payapp/transaction_list.html'
    
transaction_list = TransactionList.as_view()

        