from dj_rest_auth.registration.views import RegisterView
from django.urls import path
from rest_framework.routers import DefaultRouter
from dj_rest_auth.registration.views import (
    ResendEmailVerificationView,
    VerifyEmailView,
)
from dj_rest_auth.views import (
    LoginView,
    LogoutView,
    UserDetailsView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from allauth.socialaccount.views import signup
from users.views import (
    UserViewSet,
    UserPreferencesViewSet,
    EventTimeViewSet,
    GoogleLogin,
    email_confirm_redirect,
    password_reset_confirm_redirect,
    user_dashboard,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"user_preferences", UserPreferencesViewSet, basename="user-preference")
router.register(r"event_times", EventTimeViewSet, basename="event-time")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="rest_register"),
    path("login/", LoginView.as_view(), name="rest_login"),
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path("dashboard/", user_dashboard, name="user-dashboard"),
    path("user/", UserDetailsView.as_view(), name="rest_user_details"),
    path("signup/", signup, name="socialaccount_signup"),
    path("google/", GoogleLogin.as_view(), name="google_login"),
    path("register/verify-email/", VerifyEmailView.as_view(), name="rest_verify_email"),
    path(
        "register/resend-email/",
        ResendEmailVerificationView.as_view(),
        name="rest_resend_email",
    ),
    path(
        "account-confirm-email/<str:key>/",
        email_confirm_redirect,
        name="account_confirm_email",
    ),
    path(
        "account-confirm-email/",
        VerifyEmailView.as_view(),
        name="account_email_verification_sent",
    ),
    path("password/reset/", PasswordResetView.as_view(), name="rest_password_reset"),
    path(
        "password/reset/confirm/<str:uidb64>/<str:token>/",
        password_reset_confirm_redirect,
        name="password_reset_confirm",
    ),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]

urlpatterns += router.urls
