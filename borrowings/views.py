import os
from datetime import date
import requests
from dotenv import load_dotenv

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from Library.permissions import IsAdminOrIfAuthenticatedReadOnly
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListSerializer, BorrowingRetrieveSerializer, BorrowingCreateSerializer, \
    BorrowingReturnSerializer


load_dotenv()


def text_telegram(text):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        print("Telegram not configured. Message:", text)
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    resp = requests.post(url, data={"chat_id": chat_id, "text": text})


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_staff:
            return queryset.select_related("book")
        return queryset.filter(user=self.request.user).select_related("book")

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        elif self.action == "create":
            return BorrowingCreateSerializer
        elif self.action == "return_book":
            return BorrowingReturnSerializer
        return BorrowingRetrieveSerializer


    def perform_create(self, serializer):
        book = serializer.validated_data["book"]
        if book.inventory <= 0:
            raise ValidationError("This book is not available")

        book.inventory -= 1
        book.save()

        serializer.save(user=self.request.user)

        text_telegram(
            f"User: {self.request.user} take book {book.title}"
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="return",
    )
    def return_book(self, request, pk=None):
        borrowing = Borrowing.objects.get(pk=pk)
        if borrowing.actual_return_date is not None:
            return Response(
                {"detail": "Book already returned"},
                status=status.HTTP_400_BAD_REQUEST
            )
        borrowing.actual_return_date = date.today()
        borrowing.book.inventory += 1
        borrowing.book.save()
        borrowing.save()

        text_telegram(
            f"User {self.request.user} return book {borrowing.book.title}"
        )

        return Response(
            {"detail": "Book returned"},
            status=status.HTTP_200_OK
        )
