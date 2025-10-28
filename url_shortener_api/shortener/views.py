from django.shortcuts import get_object_or_404, redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ShortURL
from .serializers import ShortURLSerializer


class ShortenURLView(APIView):
    def post(self, request):
        serializer = ShortURLSerializer(data=request.data)

        if serializer.is_valid():
            original_url = serializer.validated_data["original_url"]

            try:
                short_url_obj, created = ShortURL.objects.get_or_create(
                    original_url=original_url
                )
            except ValueError as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            return Response(
                {
                    "original_url": short_url_obj.original_url,
                    "short_code": short_url_obj.short_code,
                    "short_url": short_url_obj.short_url,
                },
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RedirectToTargetOriginalURL(APIView):
    def get(self, request, short_code):
        short_url_obj = get_object_or_404(ShortURL, short_code=short_code)
        return redirect(short_url_obj.original_url)
