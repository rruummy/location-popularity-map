from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from reviews.models import Review, ReviewVote
from reviews.serializers import ReviewSerializer, ReviewVoteSerializer
from users.permissions import IsOwnerOrAdmin


class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )


class ReviewRetrieveUpdateDestroyView(
    generics.RetrieveUpdateDestroyAPIView
):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [
            IsAuthenticated(),
            IsOwnerOrAdmin(),
        ]


class ReviewVoteCreateView(generics.CreateAPIView):
    queryset = ReviewVote.objects.all()
    serializer_class = ReviewVoteSerializer
    permission_classes = [IsAuthenticated]

    def get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs["review_id"]
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()

        context["review"] = self.get_review()

        return context

    def perform_create(self, serializer):
        serializer.save(
            review=self.get_review(),
            user=self.request.user,
        )
