from django.http import HttpResponse
from django.shortcuts import redirect,render
from django.views.generic import FormView, View, CreateView
from django.contrib.auth.views import LoginView  
from register.forms import RegistrationForm, OnlineAccountForm, LoginForm, AdministratorCreationForm
from register.models import OnlineAccount, User, Administrator
from payapp.models import CurrencyConversion
from django.urls import reverse_lazy
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from webapps2024.utils.choices import CURRENCY_CHOICES
from webapps2024.utils.manual_exchange_rate import MANUAL_EXCHANGE_RATES
from django.contrib.auth import get_user_model
# Create your views here.

# --------------------------------------------------------- SignUP ------------------------------------------------------------------------------------------
class SignUpView(FormView):
    template_name = "register/signup.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("register:online_account_views")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.email = form.cleaned_data['email']  # Set email separately
        user.save()

        # Log in the user
        login(self.request, user)
        self.request.session['user_id'] = user.id  # Store user ID in session

        return super().form_valid(form)

    # adding widgets
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['currency_choices'] = CURRENCY_CHOICES
        return context
    
signup_view = SignUpView.as_view()


# --------------------------------------------------------- Online Account ------------------------------------------------------------------------------------------
class OnlineAccountSetupViews(LoginRequiredMixin, FormView):
    login_url = reverse_lazy('register:login_view')
    template_name = "register/online_account_setup.html"
    form_class = OnlineAccountForm
    success_url = "/"

    def form_valid(self, form):
        # Retrieve the logged-in user
        user = self.request.user

        # Fetch the appropriate exchange rate for the selected currency
        selected_currency = form.cleaned_data['currency']
        try:
            # Fetch the CurrencyConversion object for the selected currency
            conversion_rate = CurrencyConversion.objects.get(currency_to=selected_currency)

            # Calculate the initial amount based on the baseline amount and exchange rate
            baseline_amount = 1000  
            initial_amount = baseline_amount * conversion_rate.exchange_rate

        except CurrencyConversion.DoesNotExist:
            # Handle the case where conversion rate for the selected currency doesn't exist
            manual_exchange_rate = MANUAL_EXCHANGE_RATES.get(("USD", selected_currency))
            if manual_exchange_rate is not None:
                # Calculate the initial amount using the manual exchange rate
                baseline_amount = 1000  
                initial_amount = baseline_amount * manual_exchange_rate

            else:
                # Handle the case where neither automatic nor manual conversion rates are available
                error_message = "Conversion rate for the selected currency is not available."
                return self.render_to_response(self.get_context_data(form=form, error_message=error_message))

        # Create or update the OnlineAccount for the user
        online_account, created = OnlineAccount.objects.get_or_create(user=user)
        online_account.currency = selected_currency
        online_account.balance = initial_amount
        online_account.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['currency_choices'] = CURRENCY_CHOICES
        return context

    def get(self, request, *args, **kwargs):
        # Handle GET requests to clear any existing error messages
        return super().get(request, *args, **kwargs)



online_account_views = OnlineAccountSetupViews.as_view()


# --------------------------------------------------------- Login ------------------------------------------------------------------------------------------
class LoginView(FormView):
    template_name = "register/login.html"
    form_class = LoginForm

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        user = authenticate(self.request, email=email, password=password)
        if user is not None:
            login(self.request, user)
            return redirect("homepage")
        else:
            # Redirecting with an error message for invalid user
            return self.form_invalid(form)

    def form_invalid(self, form):
        email_errors = form.errors.get('email')
        password_errors = form.errors.get('password')

        if email_errors and 'required' not in email_errors:
            error = 'Invalid email.'
        elif password_errors and 'required' not in password_errors:
            error = 'Invalid password.'
        else:
            error = 'Invalid form submission'

        return render(self.request, self.template_name, {'form': form, 'error': error})
login_view = LoginView.as_view()



# --------------------------------------------------------- Logout ------------------------------------------------------------------------------------------
class LogoutView(LoginRequiredMixin, View):
    login_url = reverse_lazy('register:login_view')
    def get(self, request):
        return render(request, 'register/logout.html')

    def post(self, request):
        logout(request)
        return redirect('/')

logout_view = LogoutView.as_view()



# --------------------------------------------------------- Admin Registration ------------------------------------------------------------------------------------------


class AdministratorCreateView(CreateView):
    model = get_user_model()
    form_class = AdministratorCreationForm
    template_name = 'register/admin_register.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        login(self.request, user)  # Log in the user immediately after registration
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the Django admin index page
        return reverse_lazy('admin:index')

register_admin = AdministratorCreateView.as_view()