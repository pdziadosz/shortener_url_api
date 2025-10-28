from django.contrib import admin

from .models import ShortURL


@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = ("original_url", "short_code", "short_url", "created_at")
    readonly_fields = ("short_code", "short_url", "created_at")
