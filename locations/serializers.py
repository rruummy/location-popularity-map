from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta

from rest_framework import serializers

from locations.models import Locations

class LocationsSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(
        source="created_by.username"
    )

    rating = serializers.SerializerMethodField()
    popularity = serializers.SerializerMethodField()

    class Meta:
        model = Locations
        fields = [
            "id",
            "title",
            "description",
            "category",
            "address",
            "latitude",
            "longitude",
            "created_by",
            "created_at",
            "updated_at",
            "rating",
            "popularity",
        ]

        read_only_fields = [
            "created_by",
            "created_at",
            "updated_at",
            "rating",
            "popularity",
        ]
    def get_rating(self, obj):
        result = obj.reviews.aggregate(
            average_rating=Avg("rating")
        )

        return round(result["average_rating"] or 0, 2)

    def get_popularity(self, obj):
        seven_days_ago = timezone.now() - timedelta(days=7)

        average_rating = obj.reviews.aggregate(
            average=Avg("rating")
        )["average"] or 0

        reviews_count = obj.reviews.filter(
            created_at__gte=seven_days_ago
        ).count()

        views_count = obj.views.filter(
            created_at__gte=seven_days_ago
        ).count()

        popularity = (
            average_rating * 2
            + reviews_count
            + views_count * 0.5
        )

        return round(popularity, 2)
    def validate_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError(
                "Latitude must be between -90 and 90."
            )
        return value

    def validate_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError(
                "Longitude must be between -180 and 180."
            )
        return value

