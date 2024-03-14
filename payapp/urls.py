from django.urls import path 

from . import views

urlpatterns = [
    path("", views.home_page, name="homepage"),
    path("account", views.account, name="account"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("addbank", views.addbank, name="addbank"),
    path("withdraw", views.withdraw, name="withdraw"),
    path("withdraw/confirm", views.withdraw_money_confirm, name="withdraw_money_confirm"),
    path("withdraw/success", views.SuccessView.as_view(), name="withdraw_success"),
]
