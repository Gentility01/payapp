from django.http import HttpResponse
from django.shortcuts import redirect,render
from django.views.generic import FormView, View
from django.contrib.auth.views import LoginView , LogoutView 
from register.forms import RegistrationForm, OnlineAccountForm, LoginForm
from register.models import OnlineAccount, User
from django.urls import reverse_lazy
from django.contrib.auth import login, logout, authenticate
# Create your views here.

class SignUpView(FormView):
    template_name = "register/signup.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("register:online_account_views")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.save()
        
        # Log in the user
        login(self.request, user)
        self.request.session['user_id'] = user.id  # Store user ID in session
        
        return super().form_valid(form)
    
signup_view = SignUpView.as_view()


class OnlineAccountSetupViews(FormView):
    template_name = "register/online_account_setup.html"
    form_class = OnlineAccountForm
    success_url = "/"

    def form_valid(self, form):
        user_id = self.request.session.get('user_id')  # Retrieve user ID from session
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                if not OnlineAccount.objects.filter(user=user).exists():
                    OnlineAccount.objects.create(user=user, currency=form.cleaned_data['currency'])
            except User.DoesNotExist:
                return redirect('error_page')  # Redirect to an error page if user doesn't exist
        return super().form_valid(form)

online_account_views = OnlineAccountSetupViews.as_view()

# Login view
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

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('logout_success')
    else:
        return render(request, 'register/logout.html')