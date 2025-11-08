from django.urls import path

from payments.views import (
    CreatePaymentView,
    PaymentSuccessView,
    PaymentCancelView
)


app_name = "payments"

urlpatterns = [
    path("create/", CreatePaymentView.as_view(), name="create-payment"),
    path("success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
]
