from datetime import date

from borrowings.models import Borrowing
from borrowings.views import text_telegram


def overdue_books():
    borrowing_overdue = Borrowing.objects.filter(
        actual_return_date__isnull=True,
        expected_return_date__lte=date.today()
    )
    for borrowing in borrowing_overdue:
        text_telegram(
            f"User {borrowing.user} overdue book {borrowing.book.title}"
        )
