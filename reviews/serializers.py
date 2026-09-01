from rest_framework import serializers
from reviews.models import Review, ReviewVote


class ReviewSerializer(serializers.ModelSerializer):

    user = serializers.ReadOnlyField(
        source="user.username"
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "location",
            "user",
            "rating",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        request = self.context["request"]
        location = attrs["location"]

        if Review.objects.filter(
            location=location,
            user=request.user,
        ).exists():
            raise serializers.ValidationError(
                {
                    "location": (
                        "You have already reviewed this location."
                    )
                }
            )

        return attrs

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5."
            )

        return value


class ReviewVoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReviewVote
        fields = [
            "id",
            "review",
            "vote",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "review",
            "created_at",
        ]

    def validate(self, attrs):
        request = self.context["request"]
        review = self.context["review"]

        if ReviewVote.objects.filter(
            review=review,
            user=request.user,
        ).exists():
            raise serializers.ValidationError(
                {
                    "review": (
                        "You have already voted for this review."
                    )
                }
            )

        return attrs

    def validate_vote(self, value):
        if value not in [
            ReviewVote.LIKE,
            ReviewVote.DISLIKE,
        ]:
            raise serializers.ValidationError(
                "Vote must be either 'like' or 'dislike'."
            )

        return value
