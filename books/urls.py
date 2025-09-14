from django.urls import include, path
from rest_framework import routers

from books.views import BookViewSet

app_name = "books"


router = routers.DefaultRouter()

router.register("", BookViewSet, basename="books")
urlpatterns = [
    path("", include(router.urls)),
]
