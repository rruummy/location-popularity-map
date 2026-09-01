import django_filters
from locations.models import Locations


class LocationsFilter(django_filters.FilterSet):
    min_views = django_filters.NumberFilter(
        field_name="views_count",
        lookup_expr="gte",
    )

    class Meta:
        model = Locations
        fields = [
            "category",
            "created_by",
        ]