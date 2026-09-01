from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from categories.models import Categories
from categories.serializers import CategoriesSerializer


class CategoriesListCreateView(generics.ListCreateAPIView):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [IsAuthenticated()]


class CategoriesRetrieveUpdateDestroyView(
    generics.RetrieveUpdateDestroyAPIView
):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [IsAuthenticated()]