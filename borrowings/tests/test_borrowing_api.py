from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from books.tests.test_book_api import book_sample
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListSerializer, BorrowingRetrieveSerializer

BORROWING_LIST_URL = reverse("borrowings:borrowings-list")


def borrowings_retrieve_url(borrowing_id):
    return reverse("borrowings:borrowings-detail", args=[borrowing_id])


def borrowing_sample(**params):
    book = book_sample()
    user, created = get_user_model().objects.get_or_create(
        email="test@test.com",
        defaults={"password": "12345"}
    )

    defaults = {
        "expected_return_date": date.today() + timedelta(days=14),
        "book": book,
        "user": user
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


class UnauthenticatedBorrowingsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_borrowing_list_auth_required(self):
        res = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_borrowing_retrieve_auth_required(self):
        borrowing = borrowing_sample()
        url = borrowings_retrieve_url(borrowing.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test11@test.com",
            password="12345",
        )
        self.client.force_authenticate(user=self.user)

    def test_borrowing_list(self):
        borrowing_1 = borrowing_sample(user=self.user)
        borrowing_2 = borrowing_sample(user=self.user)
        borrowings = [borrowing_1, borrowing_2]

        res = self.client.get(BORROWING_LIST_URL)

        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_borrowing_list_forbidden(self):
        book = book_sample()
        user, created = get_user_model().objects.get_or_create(
            email="test@test.com",
            defaults={"password": "12345"}
        )

        payload = {
            "expected_return_date": date.today() + timedelta(days=14),
            "book": book,
            "user": user
        }
        res = self.client.post(BORROWING_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_borrowing_retrieve(self):
        borrowing = borrowing_sample(user=self.user)

        res = self.client.get(borrowings_retrieve_url(borrowing.id))
        serializer = BorrowingRetrieveSerializer(borrowing)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
