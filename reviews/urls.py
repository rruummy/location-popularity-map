from django.urls import path

from reviews.views import (
    ReviewListCreateView,
    ReviewRetrieveUpdateDestroyView,
    ReviewVoteCreateView,
)

urlpatterns = [
    path("", ReviewListCreateView.as_view()),
    path("<int:pk>/", ReviewRetrieveUpdateDestroyView.as_view()),
    path("<int:review_id>/vote/", ReviewVoteCreateView.as_view()),
]