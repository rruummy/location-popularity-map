from django.core.cache import cache

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from locations.models import Locations, LocationView
from locations.serializers import LocationsSerializer

from users.permissions import IsOwnerOrAdmin


class LocationsListCreateView(generics.ListCreateAPIView):
    queryset = Locations.objects.all()
    serializer_class = LocationsSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user
        )

class LocationsRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
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
