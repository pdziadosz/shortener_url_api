from django.urls import path

from .views import RedirectToTargetOriginalURL, ShortenURLView

urlpatterns = [
    path("", ShortenURLView.as_view(), name="shorten-url"),
    path(
        "<str:short_code>/",
        RedirectToTargetOriginalURL.as_view(),
        name="redirect-original",
    ),
]
