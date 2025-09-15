from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from books.models import Book
from books.serializers import BookListSerializer, BookRetrieveSerializer


BOOK_LIST_URL = reverse("books:books-list")


def book_retrieve_url(book_id):
    return reverse("books:books-detail", args=[book_id])


def book_sample(**params):
    defaults = {
        "title": "1984",
        "author": "George Orwell",
        "cover": "HARD",
        "inventory": 5,
        "daily_fee": 1.5
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


class UnauthenticatedBooksApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_book_list_auth_required(self):
        res = self.client.get(BOOK_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_book_retrieve_auth_required(self):
        book = book_sample()
        url = book_retrieve_url(book.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBooksApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="12345",
        )
        self.client.force_authenticate(user=self.user)

    def test_books_list(self):
        book_1 = book_sample()
        book_2 = book_sample()
        books = [book_1, book_2]

        res = self.client.get(BOOK_LIST_URL)

        serializer = BookListSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_books_list_forbidden(self):
        payload = {
            "title": "test",
            "author": "George Orwell",
            "cover": "HARD",
            "inventory": 5,
            "daily_fee": 1.5
        }
        res = self.client.post(BOOK_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_books_retrieve(self):
        book = book_sample()

        res = self.client.get(book_retrieve_url(book.id))
        serializer = BookRetrieveSerializer(book)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
