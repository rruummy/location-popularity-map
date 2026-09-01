from django.urls import path

from reviews.views import (
    ReviewListCreateView,
    ReviewRetrieveUpdateDestroyView,
    ReviewVoteCreateView,
)


urlpatterns = [
    path("", ReviewListCreateView.as_view(), name="reviews-list"),
    path("<int:pk>/", ReviewRetrieveUpdateDestroyView.as_view(), name="reviews-detail"),
    path("<int:review_id>/vote/", ReviewVoteCreateView.as_view(), name="reviews-vote"),
]