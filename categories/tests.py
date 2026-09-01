from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from categories.models import Categories


User = get_user_model()


class CategoriesAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
        )

        self.category = Categories.objects.create(
            title="Restaurants"
        )

        self.list_url = reverse("categories-list")
        self.detail_url = reverse(
            "categories-detail",
            kwargs={"pk": self.category.pk},
        )

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    # -------------------------
    # GET LIST
    # -------------------------

    def test_get_categories(self):
        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        # Якщо використовується pagination
        self.assertEqual(
            response.data["count"],
            Categories.objects.count(),
        )

    # -------------------------
    # GET DETAIL
    # -------------------------

    def test_get_category_detail(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.category.id,
        )

        self.assertEqual(
            response.data["title"],
            "Restaurants",
        )

    # -------------------------
    # POST
    # -------------------------

    def test_create_category(self):
        self.authenticate()

        data = {
            "title": "Hotels"
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

        self.assertTrue(
            Categories.objects.filter(
                title="Hotels"
            ).exists()
        )

    # -------------------------
    # POST DUPLICATE
    # -------------------------

    def test_create_duplicate_category(self):
        self.authenticate()

        data = {
            "title": "Restaurants"
        }

        response = self.client.post(
            self.list_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "title",
            response.data,
        )

    # -------------------------
    # PATCH
    # -------------------------

    def test_update_category(self):
        self.authenticate()

        response = self.client.patch(
            self.detail_url,
            {
                "title": "Updated category"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.category.refresh_from_db()

        self.assertEqual(
            self.category.title,
            "Updated category",
        )

    # -------------------------
    # PATCH DUPLICATE
    # -------------------------

    def test_update_category_to_duplicate_title(self):
        self.authenticate()

        second_category = Categories.objects.create(
            title="Hotels"
        )

        response = self.client.patch(
            reverse(
                "categories-detail",
                kwargs={"pk": second_category.pk},
            ),
            {
                "title": "Restaurants"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "title",
            response.data,
        )

    # -------------------------
    # DELETE
    # -------------------------

    def test_delete_category(self):
        self.authenticate()

        response = self.client.delete(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Categories.objects.filter(
                pk=self.category.pk
            ).exists()
        )

    # -------------------------
    # NOT FOUND
    # -------------------------

    def test_get_nonexistent_category(self):
        response = self.client.get(
            reverse(
                "categories-detail",
                kwargs={"pk": 999999},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # -------------------------
    # UNAUTHENTICATED POST
    # -------------------------

    def test_create_category_unauthenticated(self):
        response = self.client.post(
            self.list_url,
            {
                "title": "Hotels"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # -------------------------
    # UNAUTHENTICATED PATCH
    # -------------------------

    def test_update_category_unauthenticated(self):
        response = self.client.patch(
            self.detail_url,
            {
                "title": "Updated"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # -------------------------
    # UNAUTHENTICATED DELETE
    # -------------------------

    def test_delete_category_unauthenticated(self):
        response = self.client.delete(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )