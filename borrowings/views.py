from datetime import date

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListSerializer, BorrowingRetrieveSerializer, BorrowingCreateSerializer, \
    BorrowingReturnSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_staff:
            return queryset
        else:
            return queryset.filter(user=self.request.user)

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

        return Response(
            {"detail": "Book returned"},
            status=status.HTTP_200_OK
        )
