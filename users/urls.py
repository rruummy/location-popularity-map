from django.urls import path

from users.views import RegisterView, LoginView, LogoutView, MeView, PasswordResetView, PasswordResetConfirmView

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("me/", MeView.as_view()),
    path("password-reset/", PasswordResetView.as_view()),
    path("password-reset-confirm/", PasswordResetConfirmView.as_view()),
]   