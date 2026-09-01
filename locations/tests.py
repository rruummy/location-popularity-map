import json

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from categories.models import Categories
from locations.models import Locations


User = get_user_model()


class LocationsAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            password="testpassword",
        )

        self.category = Categories.objects.create(
            title="Cafe",
        )

        self.other_category = Categories.objects.create(
            title="Restaurant",
        )

        self.location = Locations.objects.create(
            title="Coffee Lviv",
            description="A nice coffee shop in Lviv",
            category=self.category,
            address="Lviv",
            latitude=49.8397,
            longitude=24.0297,
            created_by=self.user,
        )

        self.other_location = Locations.objects.create(
            title="Restaurant Kyiv",
            description="A restaurant in Kyiv",
            category=self.other_category,
            address="Kyiv",
            latitude=50.4501,
            longitude=30.5234,
            created_by=self.other_user,
        )

        self.list_url = reverse("locations-list")

    def test_get_locations(self):
        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_search_locations(self):
        response = self.client.get(
            self.list_url,
            {"search": "Coffee"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        self.assertEqual(
            response.data["results"][0]["title"],
            "Coffee Lviv",
        )

    def test_filter_locations_by_category(self):
        response = self.client.get(
            self.list_url,
            {"category": self.category.id},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        self.assertEqual(
            response.data["results"][0]["title"],
            "Coffee Lviv",
        )

    def test_filter_locations_by_author(self):
        response = self.client.get(
            self.list_url,
            {"created_by": self.user.id},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        self.assertEqual(
            response.data["results"][0]["title"],
            "Coffee Lviv",
        )

    def test_create_location(self):
        self.client.force_authenticate(
            user=self.user
        )

        data = {
            "title": "New Location",
            "description": "New location description",
            "category": self.category.id,
            "address": "Lviv",
            "latitude": 49.8400,
            "longitude": 24.0300,
        }

        response = self.client.post(
            self.list_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            Locations.objects.count(),
            3,
        )

        self.assertEqual(
            Locations.objects.get(
                title="New Location"
            ).created_by,
            self.user,
        )

    def test_create_location_requires_authentication(self):
        data = {
            "title": "New Location",
            "description": "Description",
            "category": self.category.id,
            "address": "Lviv",
            "latitude": 49.8400,
            "longitude": 24.0300,
        }

        response = self.client.post(
            self.list_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_export_json(self):
        url = reverse("locations-export")

        response = self.client.get(
            url,
            {"format": "json"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "application/json",
            response["Content-Type"],
        )

    def test_export_csv(self):
        url = reverse("locations-export")

        response = self.client.get(
            url,
            {"format": "csv"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "text/csv",
            response["Content-Type"],
        )

    def test_export_csv_with_search(self):
        url = reverse("locations-export")

        response = self.client.get(
            url,
            {
                "format": "csv",
                "search": "Coffee",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "Coffee Lviv",
            response.content.decode("utf-8-sig"),
        )

        self.assertNotIn(
            "Restaurant Kyiv",
            response.content.decode("utf-8-sig"),
        )

    def test_export_default_format_is_json(self):
        url = reverse("locations-export")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "application/json",
            response["Content-Type"],
        )

    def test_export_unsupported_format(self):
        url = reverse("locations-export")

        response = self.client.get(
            url,
            {"format": "xml"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "error",
            response.data,
        )

    def test_export_csv_has_attachment_disposition(self):
        url = reverse("locations-export")

        response = self.client.get(
            url,
            {"format": "csv"},
        )

        self.assertIn(
            'attachment; filename="locations.csv"',
            response["Content-Disposition"],
        )

    def test_export_json_has_attachment_disposition(self):
        url = reverse("locations-export")

        response = self.client.get(
            url,
            {"format": "json"},
        )

        self.assertIn(
            'attachment; filename="locations.json"',
            response["Content-Disposition"],
        )

    def test_export_csv_contains_both_locations(self):
        url = reverse("locations-export")

        response = self.client.get(
            url,
            {"format": "csv"},
        )

        content = response.content.decode("utf-8-sig")

        self.assertIn("Coffee Lviv", content)
        self.assertIn("Restaurant Kyiv", content)

        # header row + 2 data rows
        rows = [row for row in content.splitlines() if row]
        self.assertEqual(len(rows), 3)

    def test_export_json_contains_both_locations(self):
        url = reverse("locations-export")

        response = self.client.get(
            url,
            {"format": "json"},
        )

        data = json.loads(response.content.decode("utf-8"))
        titles = {item["title"] for item in data}

        self.assertEqual(
            titles,
            {"Coffee Lviv", "Restaurant Kyiv"},
        )

    def test_export_is_not_paginated(self):
        # PAGE_SIZE is 10, so create enough locations that the
        # regular list endpoint would paginate but export should not.
        for i in range(15):
            Locations.objects.create(
                title=f"Extra location {i}",
                description="Extra",
                category=self.category,
                address="Lviv",
                latitude=49.8,
                longitude=24.0,
                created_by=self.user,
            )

        url = reverse("locations-export")

        response = self.client.get(
            url,
            {"format": "json"},
        )

        data = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(data), 17)

    def test_export_csv_filtered_by_category(self):
        url = reverse("locations-export")

        response = self.client.get(
            url,
            {
                "format": "csv",
                "category": self.other_category.id,
            },
        )

        content = response.content.decode("utf-8-sig")

        self.assertIn("Restaurant Kyiv", content)
        self.assertNotIn("Coffee Lviv", content)

    def test_export_available_without_authentication(self):
        url = reverse("locations-export")

        response = self.client.get(
            url,
            {"format": "csv"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )