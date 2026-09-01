from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from categories.models import Categories
from locations.models import Locations
from reviews.models import Review, ReviewVote


User = get_user_model()


class ReviewsAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="user",
            password="password123",
        )

        self.other_user = User.objects.create_user(
            username="other",
            password="password123",
        )

        self.category = Categories.objects.create(
            title="Cafe",
        )

        self.location = Locations.objects.create(
            title="Test Location",
            description="Test description",
            category=self.category,
            created_by=self.user,
        )

        self.review = Review.objects.create(
            location=self.location,
            user=self.user,
            rating=5,
            comment="Excellent place!",
        )

        self.reviews_url = reverse("reviews-list")
        self.review_detail_url = reverse(
            "reviews-detail",
            kwargs={"pk": self.review.id},
        )
        self.vote_url = reverse(
            "reviews-vote",
            kwargs={"review_id": self.review.id},
        )

    # --------------------------------------------------
    # GET REVIEWS
    # --------------------------------------------------

    def test_get_reviews(self):
        response = self.client.get(self.reviews_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            Review.objects.count(),
        )

    def test_get_review_detail(self):
        response = self.client.get(
            self.review_detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.review.id,
        )

        self.assertEqual(
            response.data["rating"],
            5,
        )

        self.assertEqual(
            response.data["comment"],
            "Excellent place!",
        )

    # --------------------------------------------------
    # CREATE REVIEW
    # --------------------------------------------------

    def test_create_review(self):
        self.client.force_authenticate(
            user=self.other_user
        )

        data = {
            "location": self.location.id,
            "rating": 4,
            "comment": "Good place",
        }

        response = self.client.post(
            self.reviews_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Review.objects.filter(
                location=self.location,
                user=self.other_user,
            ).exists()
        )

    def test_create_review_unauthenticated(self):
        data = {
            "location": self.location.id,
            "rating": 4,
            "comment": "Good place",
        }

        response = self.client.post(
            self.reviews_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_create_duplicate_review(self):
        self.client.force_authenticate(
            user=self.user
        )

        data = {
            "location": self.location.id,
            "rating": 4,
            "comment": "Another review",
        }

        response = self.client.post(
            self.reviews_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "location",
            response.data,
        )

    # --------------------------------------------------
    # RATING VALIDATION
    # --------------------------------------------------

    def test_create_review_with_rating_less_than_one(self):
        self.client.force_authenticate(
            user=self.other_user
        )

        data = {
            "location": self.location.id,
            "rating": 0,
            "comment": "Bad rating",
        }

        response = self.client.post(
            self.reviews_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_review_with_rating_greater_than_five(self):
        self.client.force_authenticate(
            user=self.other_user
        )

        data = {
            "location": self.location.id,
            "rating": 6,
            "comment": "Bad rating",
        }

        response = self.client.post(
            self.reviews_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------
    # UPDATE REVIEW
    # --------------------------------------------------

    def test_update_own_review(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            self.review_detail_url,
            {
                "rating": 4,
                "comment": "Updated comment",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.review.refresh_from_db()

        self.assertEqual(
            self.review.rating,
            4,
        )

        self.assertEqual(
            self.review.comment,
            "Updated comment",
        )

    def test_other_user_cannot_update_review(self):
        self.client.force_authenticate(
            user=self.other_user
        )

        response = self.client.patch(
            self.review_detail_url,
            {
                "rating": 3,
                "comment": "Hacked review",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # --------------------------------------------------
    # DELETE REVIEW
    # --------------------------------------------------

    def test_delete_own_review(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.delete(
            self.review_detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Review.objects.filter(
                id=self.review.id
            ).exists()
        )

    def test_other_user_cannot_delete_review(self):
        self.client.force_authenticate(
            user=self.other_user
        )

        response = self.client.delete(
            self.review_detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            Review.objects.filter(
                id=self.review.id
            ).exists()
        )

    # --------------------------------------------------
    # VOTES
    # --------------------------------------------------

    def test_create_like_vote(self):
        self.client.force_authenticate(
            user=self.other_user
        )

        response = self.client.post(
            self.vote_url,
            {
                "vote": ReviewVote.LIKE,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            ReviewVote.objects.filter(
                review=self.review,
                user=self.other_user,
                vote=ReviewVote.LIKE,
            ).exists()
        )

    def test_create_dislike_vote(self):
        self.client.force_authenticate(
            user=self.other_user
        )

        response = self.client.post(
            self.vote_url,
            {
                "vote": ReviewVote.DISLIKE,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            ReviewVote.objects.filter(
                review=self.review,
                user=self.other_user,
                vote=ReviewVote.DISLIKE,
            ).exists()
        )

    def test_duplicate_vote(self):
        self.client.force_authenticate(
            user=self.other_user
        )

        ReviewVote.objects.create(
            review=self.review,
            user=self.other_user,
            vote=ReviewVote.LIKE,
        )

        response = self.client.post(
            self.vote_url,
            {
                "vote": ReviewVote.DISLIKE,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "review",
            response.data,
        )

    def test_invalid_vote(self):
        self.client.force_authenticate(
            user=self.other_user
        )

        response = self.client.post(
            self.vote_url,
            {
                "vote": "something",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_unauthenticated_user_cannot_vote(self):
        response = self.client.post(
            self.vote_url,
            {
                "vote": ReviewVote.LIKE,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_vote_for_nonexistent_review(self):
        self.client.force_authenticate(
            user=self.other_user
        )

        url = reverse(
            "reviews-vote",
            kwargs={"review_id": 99999},
        )

        response = self.client.post(
            url,
            {
                "vote": ReviewVote.LIKE,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )