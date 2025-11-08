from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from borrowings.tests.test_borrowing_api import borrowing_sample
from payments.serializers import PaymentSerializer


class PaymentApiTests(TestCase):
    def test_payment_create(self):
        borrowing = borrowing_sample()
        data = {
            "money_to_pay": 10,
            "borrowing": borrowing.id,
            "type": "Payment"
        }
        serializer = PaymentSerializer(data=data)
        serializer.is_valid()
        self.assertTrue(serializer.is_valid())
        payment = serializer.save()

        self.assertEqual(payment.money_to_pay, 10)
        self.assertEqual(payment.borrowing, borrowing)

    @patch("payments.views.stripe.checkout.Session.create")
    def test_create_payment(self, mock_stripe):
        mock_stripe.return_value.id = "sess_123"
        mock_stripe.return_value.url = "http://session.url"

        borrowing = borrowing_sample()
        data = {
            "money_to_pay": 10,
            "borrowing": borrowing.id,
            "type": "Payment"
        }
        res = self.client.post(reverse("payments:create-payment"), data)

        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["session_url"], "http://session.url")
