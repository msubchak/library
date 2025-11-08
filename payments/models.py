from django.db import models

from borrowings.models import Borrowing


class Payment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "Pending"
        PAID = "Paid"

    class TypeChoices(models.TextChoices):
        PAYMENT = "Payment"
        FINE = "Fine"

    status = models.CharField(max_length=10, choices=StatusChoices.choices)
    type = models.CharField(max_length=10, choices=TypeChoices.choices)
    money_to_pay = models.DecimalField(decimal_places=2, max_digits=10)
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    session_url = models.URLField(null=True, blank=True)
