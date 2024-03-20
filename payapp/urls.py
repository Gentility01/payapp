from django.urls import path 

from . import views

urlpatterns = [
    path("", views.home_page, name="homepage"),
    path("account", views.account, name="account"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("addbank", views.addbank, name="addbank"),
    path("create_card", views.create_card, name="create_card"),
    path("withdraw", views.withdraw, name="withdraw"),
    path("withdraw/confirm", views.withdraw_money_confirm, name="withdraw_money_confirm"),
    path("withdraw/success", views.SuccessView.as_view(), name="withdraw_success"),
    path("deposite", views.deposite, name="deposite"),
    path("bank_selection", views.bank_selection, name="bank_selection"),
    path("bank_deposit_receipt/<int:pk>", views.bank_deposit_receipt, name="bank_deposit_receipt"),
    path("card_selection", views.card_selection, name="card_selection"),
    path("card_deposit_receipt/<int:pk>", views.card_deposit_receipt, name="card_deposit_receipt"),
    path("direct_payment", views.direct_payment_view, name="direct_payment_view"),
    path("direct_payment_confirmation", views.direct_payment_confirmation_view, name="payment_confirmation"),
    path("payment_success_view", views.payment_success_view, name="payment_success"),
    path("payment_failed", views.payment_failed, name="payment_failed"),
    path("payment_request", views.request_payment_view, name="payment_request_view"),
    path("payment_request_list", views.payment_request_list, name="payment_request_list"),
    path('respond_to_payment/<int:pk>/', views.RespondToPaymentRequestView.as_view(), name='respond_to_payment_request'),
    path("payment_request_success", views.payment_request_success, name="payment_request_success"),
    path("transaction_list", views.transaction_list, name="transaction_list"),
]
