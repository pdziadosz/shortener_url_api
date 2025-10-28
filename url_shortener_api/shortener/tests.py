from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .utils import generate_unique_code_from_id

from .models import ShortURL


class ShortenerUnitTests(TestCase):
    def setUp(self):
        self.valid_url = "https://example.test.com/test"

    def test_create_shorturl_model(self):
        short_url_obj = ShortURL.objects.create(original_url=self.valid_url)
        self.assertIsNotNone(short_url_obj.short_code)
        self.assertEqual(
            short_url_obj.short_url,
            f"{settings.SHORTENER_BASE_URL}/shrt/{short_url_obj.short_code}/",
        )
        self.assertEqual(short_url_obj.original_url, self.valid_url)

    def test_duplicate_shorturl_entry(self):
        short_url_obj1 = ShortURL.objects.create(original_url=self.valid_url)
        short_url_obj2, created = ShortURL.objects.get_or_create(
            original_url=self.valid_url
        )
        self.assertEqual(short_url_obj1.id, short_url_obj2.id)
        self.assertFalse(created)

    @patch("shortener.models.generate_unique_code_from_id")
    def test_unique_code_failure_raises_value_error(self, mock_generate):
        fixed_short_code = "12345678"
        mock_generate.return_value = fixed_short_code
        ShortURL.objects.create(
            original_url=self.valid_url, short_code=fixed_short_code
        )

        with self.assertRaises(ValueError):
            ShortURL.objects.create(original_url="https://example.com/second")

    def test_generate_unique_code_from_id_length(self):
        code = generate_unique_code_from_id(obj_id=1, code_length=8)
        self.assertEqual(len(code), 8)


class ShortenerE2ETests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_url = "https://example.test.com/test"
        self.invalid_url = "invalid_url"

    def test_shorten_url_api_success(self):
        response = self.client.post(
            reverse("shorten-url"), {"original_url": self.valid_url}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("short_code", response.data)
        self.assertIn("short_url", response.data)
        self.assertEqual(response.data["original_url"], self.valid_url)

    def test_shorten_url_api_duplicate(self):
        obj = ShortURL.objects.create(original_url=self.valid_url)
        response = self.client.post(
            reverse("shorten-url"), {"original_url": self.valid_url}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["short_code"], obj.short_code)

    def test_shorten_url_api_invalid(self):
        response = self.client.post(
            reverse("shorten-url"), {"original_url": self.invalid_url}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("original_url", response.data)

    def test_redirect_short_url_success(self):
        obj = ShortURL.objects.create(original_url=self.valid_url)
        response = self.client.get(reverse("redirect-original", args=[obj.short_code]))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, self.valid_url)
