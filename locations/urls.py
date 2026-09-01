from django.urls import path

from locations.views import (LocationsListCreateView,
                             LocationsRetrieveUpdateDestroyView,
                             LocationsExportView)


urlpatterns = [
    path("", LocationsListCreateView.as_view(), name="locations-list"),
    path("export/", LocationsExportView.as_view(), name="locations-export"),
    path("<int:pk>/", LocationsRetrieveUpdateDestroyView.as_view(), name="locations-detail"),
]