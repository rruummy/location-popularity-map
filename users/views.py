from django.contrib.auth.models import User
from django.contrib.auth import login, logout

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from users.serializers import (RegisterSerializer,
                               LoginSerializer,
                               PasswordResetSerializer,
                               PasswordResetConfirmSerializer,)



class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = []

class LoginView(APIView):
    permission_classes = []

    @extend_schema(
        summary="Login user",
        description="Authenticate user using Django Session Authentication.",
        request=LoginSerializer,
        responses={200: dict},
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        login(request, user)

        return Response(
            {
                "message": "Successfully logged in"
            },
            status=status.HTTP_200_OK,
        )

class LogoutView(APIView):

    def post(self, request):
        logout(request)

        return Response(
            {
                "message": "Successfully logged out"
            },
            status=status.HTTP_200_OK,
        )
    
class MeView(APIView):

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
        })

class PasswordResetView(APIView):
    permission_classes = []

    @extend_schema(
        summary="Request password reset",
        request=PasswordResetSerializer,
        responses={200: dict},
    )
    def post(self, request):
        serializer = PasswordResetSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "If an account with this email exists, "
                           "a password reset link has been sent."
            },
            status=status.HTTP_200_OK,
        )

class PasswordResetConfirmView(APIView):
    permission_classes = []
    @extend_schema(
        summary="Request password reset",
        request=PasswordResetConfirmSerializer,
        responses={200: dict},
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            user_id = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"detail": "Invalid reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired reset token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password has been successfully reset."},
            status=status.HTTP_200_OK,
        )