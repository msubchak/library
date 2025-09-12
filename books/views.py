from django.shortcuts import render
from rest_framework import viewsets

from Library.permissions import IsAdminOrIfAuthenticatedReadOnly
from books.models import Book
from books.serializers import BookListSerializer, BookRetrieveSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        return BookRetrieveSerializer
