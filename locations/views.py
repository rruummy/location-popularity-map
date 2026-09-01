import json

import pandas as pd

from django.core.cache import cache
from django.db.models import Count
from django.http import HttpResponse

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, generics, status
from rest_framework.negotiation import DefaultContentNegotiation
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from locations.cache import clear_locations_cache
from locations.models import Locations, LocationView
from locations.serializers import LocationsSerializer
from users.permissions import IsOwnerOrAdmin


class LocationFilterMixin:
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "category",
        "created_by",
    ]

    search_fields = [
        "title",
        "description",
    ]

    ordering_fields = [
        "created_at",
        "popularity",
    ]

    ordering = [
        "-created_at",
    ]

    def get_queryset(self):
        return Locations.objects.annotate(
            popularity=Count("views")
        )


class LocationsListCreateView(
    LocationFilterMixin,
    generics.ListCreateAPIView,
):
    serializer_class = LocationsSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        cache_key = (
            f"locations:list:"
            f"{request.get_full_path()}"
        )

        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        queryset = self.filter_queryset(
            self.get_queryset()
        )

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
            )

            response = self.get_paginated_response(
                serializer.data
            )

            cache.set(
                cache_key,
                response.data,
                timeout=60 * 5,
            )

            return response

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        cache.set(
            cache_key,
            serializer.data,
            timeout=60 * 5,
        )

        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user
        )

        clear_locations_cache()


class LocationsRetrieveUpdateDestroyView(
    generics.RetrieveUpdateDestroyAPIView,
):
    queryset = Locations.objects.all()
    serializer_class = LocationsSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [
            IsAuthenticated(),
            IsOwnerOrAdmin(),
        ]

    def retrieve(self, request, *args, **kwargs):
        location = self.get_object()

        self.register_view(location)

        return super().retrieve(
            request,
            *args,
            **kwargs,
        )

    def register_view(self, location):
        if not self.request.user.is_authenticated:
            return

        cache_key = (
            f"location_view:"
            f"{location.id}:"
            f"user:{self.request.user.id}"
        )

        if cache.get(cache_key):
            return

        LocationView.objects.create(
            location=location,
            user=self.request.user,
        )

        cache.set(
            cache_key,
            True,
            timeout=60 * 60,
        )

        clear_locations_cache()

    def perform_update(self, serializer):
        serializer.save()

        clear_locations_cache()

    def perform_destroy(self, instance):
        instance.delete()

        clear_locations_cache()


class ExportContentNegotiation(DefaultContentNegotiation):
    """
    By default, DRF reads the `?format=` query param itself (see
    `URL_FORMAT_OVERRIDE` / `DefaultContentNegotiation.select_renderer`)
    and raises Http404 whenever that value doesn't match one of the
    view's registered renderers. Since only JSON is registered by
    default, `?format=csv` (and any other value) was being rejected
    with a 404 before `LocationsExportView.get()` ever ran.

    This view builds its response manually for every format it
    supports (see `export_json` / `export_csv`) and returns its own
    400 for anything else, so we don't want DRF's renderer-based
    format filtering here at all - just always negotiate normally.
    """

    def select_renderer(self, request, renderers, format_suffix=None):
        return (renderers[0], renderers[0].media_type)


class LocationsExportView(
    LocationFilterMixin,
    generics.GenericAPIView,
):

    serializer_class = LocationsSerializer
    permission_classes = [AllowAny]
    content_negotiation_class = ExportContentNegotiation

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        queryset = self.filter_queryset(queryset)

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        data = serializer.data

        export_format = request.query_params.get(
            "format",
            "json",
        ).lower()

        if export_format == "json":
            return self.export_json(data)

        if export_format == "csv":
            return self.export_csv(data)

        return Response(
            {
                "error": (
                    "Unsupported format. "
                    "Use 'json' or 'csv'."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def export_json(self, data):
        response = HttpResponse(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=4,
                default=str,
            ),
            content_type="application/json; charset=utf-8",
        )

        response["Content-Disposition"] = (
            'attachment; filename="locations.json"'
        )

        return response

    def export_csv(self, data):
        dataframe = pd.DataFrame(data)

        response = HttpResponse(
            content_type="text/csv; charset=utf-8",
        )

        response["Content-Disposition"] = (
            'attachment; filename="locations.csv"'
        )

        response.write("\ufeff")

        dataframe.to_csv(
            response,
            index=False,
        )

        return response