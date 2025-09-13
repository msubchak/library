import stripe
from rest_framework import viewsets
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(borrowing__user=self.request.user)


class CreatePaymentView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save(status="Pending")

        stripe.api_key = settings.STRIPE_SECRET_KEY

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"Borrowing {payment.borrowing.id}"},
                    "unit_amount": int(payment.money_to_pay * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=request.build_absolute_uri(
                "/api/payments/success/?session_id={CHECKOUT_SESSION_ID}"
            ),
            cancel_url=request.build_absolute_uri("/api/payments/cancel/"),
        )

        payment.session_id = session.id
        payment.session_url = session.url
        payment.save()

        return Response({"session_url": payment.session_url}, status=status.HTTP_201_CREATED)



class PaymentSuccessView(APIView):
    def get(self, request, *args, **kwargs):
        session_id = request.GET.get("session_id")
        try:
            payment = Payment.objects.get(session_id=session_id)
            payment.status = "PAID"
            payment.save()
            return Response({"message": "Payment successful"}, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)


class PaymentCancelView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Payment cancelled"}, status=status.HTTP_200_OK)
