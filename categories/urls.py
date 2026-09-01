from django.urls import path

from categories.views import CategoriesListCreateView, CategoriesRetrieveUpdateDestroyView


urlpatterns = [
    path("", CategoriesListCreateView.as_view(), name="categories-list"),
    path("<int:pk>/", CategoriesRetrieveUpdateDestroyView.as_view(), name="categories-detail"),
]