from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, FormView
from register.models import  BankAccount,OnlineAccount
from payapp.models import TransactionHistory
from payapp.forms import BankAccountForm, WithdrawalForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


# Create your views here.

class HomePageView(TemplateView):
    template_name = "payapp/index.html"

home_page = HomePageView.as_view()



class AccountViews(TemplateView):
    template_name = "payapp/account.html"
   
account =  AccountViews.as_view()




class  DashboardView(TemplateView):
    template_name = "payapp/dashboard.html"

dashboard = DashboardView.as_view()

class Addbank(CreateView):
    model = BankAccount
    form_class = BankAccountForm
    template_name = 'payapp/addbank.html'
    success_url = reverse_lazy('dashboard')  # Redirect to a success URL

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


addbank = Addbank.as_view()


class WithdrawalView(FormView):
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
                    user=request.user, description='Withdrawal to bank account',
                     status='-', amount=amount)

                del request.session['withdrawal_details']
                messages.success(request, 'Withdrawal successful')
                return redirect('withdraw_success')
            else:
                messages.error(request, 'Insufficient balance')
        return self.render_to_response(self.get_context_data(request=request, form=form))

withdraw_money_confirm = ConfirmationView.as_view()

class SuccessView(TemplateView):
    template_name = 'payapp/withdrawal_success.html'