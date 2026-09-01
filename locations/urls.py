from django.urls import path

from locations.views import LocationsListCreateView, LocationsRetrieveUpdateDestroyView


urlpatterns = [
    path("", LocationsListCreateView.as_view()),
    path("<int:pk>/", LocationsRetrieveUpdateDestroyView.as_view()),
]