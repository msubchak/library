from django.urls import path

from payments.views import CreatePaymentView, PaymentSuccessView, PaymentCancelView

urlpatterns = [
    path("payments/create/", CreatePaymentView.as_view(), name="create-payment"),
    path("payments/success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("payments/cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
]
