import re
from django.http import Http404, HttpResponseRedirect
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from common.views import AsyncModelViewSet
from .models import *
from .serializers import *

import logging

logger = logging.getLogger(__name__)


def email_confirm_redirect(request, key):
    # Validate key is a UUID
    if not re.match(
        r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
        key,
    ):
        raise Http404("Invalid key format")

    return HttpResponseRedirect(f"{settings.EMAIL_CONFIRM_REDIRECT_BASE_URL}{key}/")


def password_reset_confirm_redirect(request, uidb64, token):
    # Validate uidb64 is a base64 urlsafe
    if not re.match(r"^[A-Za-z0-9_\-]+$", uidb64):
        raise Http404("Invalid uidb64 format")

    # Validate token is secure
    if not re.match(r"^[0-9A-Za-z\-_]+$", token):
        raise Http404("Invalid token format")

    return HttpResponseRedirect(
        f"{settings.PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL}{uidb64}/{token}/"
    )


class UserViewSet(AsyncModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class UserPreferencesViewSet(AsyncModelViewSet):
    queryset = UserPreferences.objects.all()
    serializer_class = UserPreferencesSerializer


class EventTimeViewSet(AsyncModelViewSet):
    queryset = EventTime.objects.all()
    serializer_class = EventTimeSerializer


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:8000/"
    client_class = OAuth2Client
