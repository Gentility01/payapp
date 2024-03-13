from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, FormView
from register.models import  BankAccount
from payapp.forms import BankAccountForm, WithdrawForm, WithdrawConfirmationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

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


