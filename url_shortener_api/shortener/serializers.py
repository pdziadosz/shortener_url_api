from rest_framework import serializers

from .models import ShortURL


class ShortURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortURL
        fields = ["original_url", "short_code", "short_url"]
        read_only_fields = ["short_code", "short_url"]
