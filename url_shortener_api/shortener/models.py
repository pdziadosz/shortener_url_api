from django.conf import settings
from django.db import IntegrityError, models, transaction

from .utils import generate_unique_code_from_id

SHORT_CODE_LENGTH = 8
MAX_GENERATION_ATTEMPTS = 5


class ShortURL(models.Model):
    original_url = models.URLField()
    short_code = models.CharField(
        max_length=8, unique=True, db_index=True, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            attempt = 0
            short_code_assigned = False

            while attempt < MAX_GENERATION_ATTEMPTS:
                code = generate_unique_code_from_id(
                    self.id, code_length=SHORT_CODE_LENGTH
                )

                try:
                    with transaction.atomic():
                        self.short_code = code
                        super().save()
                        short_code_assigned = True
                    break
                except IntegrityError:
                    attempt += 1

            if not short_code_assigned:
                raise ValueError(
                    "Unable to generate a shorten url, please try again later."
                )

    @property
    def short_url(self):
        base_url = getattr(settings, "SHORTENER_BASE_URL", "http://localhost:8000")
        return f"{base_url}/shrt/{self.short_code}/"

    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"
