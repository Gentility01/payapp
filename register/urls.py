from django.urls import path
from . import views

app_name = 'register'

urlpatterns = [
    path("register", views.signup_view, name="signup_view"),
    path("setup_online_account", views.online_account_views, name="online_account_views"),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
]

