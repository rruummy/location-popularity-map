from rest_framework import serializers
from categories.models import Categories


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ['id', 'title']

    def validate_title(self, value):
        if Categories.objects.filter(title=value).exists():
            raise serializers.ValidationError(
                "Category with this title already exists."
            )
        return value