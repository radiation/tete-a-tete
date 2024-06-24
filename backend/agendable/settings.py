import logging
import os
from datetime import timedelta
from pathlib import Path

from corsheaders.defaults import default_headers
from kombu import Queue

logger = logging.getLogger(__name__)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-#&!@")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get("DEBUG", default=0))

hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost 127.0.0.1 [::1]").split(" ")

if DEBUG:
    hosts.append(".ngrok.io")

ALLOWED_HOSTS = hosts
logger.debug("Allowed Hosts:", ALLOWED_HOSTS)

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    "social_core.backends.open_id.OpenIdAuth",
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

# Add configuration for Google provider
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
            "https://www.googleapis.com/auth/calendar",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    }
}

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "rest_framework",
    "rest_framework.authtoken",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "social_django",
    "mailer",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "corsheaders",
    "common",
    "users",
    "meetings",
    "django_celery_beat",
    "channels",
    "sslserver",
    "drf_yasg",
]

MIDDLEWARE = [
    "users.middlewares.LogMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "agendable.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ASGI_APPLICATION = "agendable.asgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("SQL_DATABASE", BASE_DIR / "db.sqlite3"),
        "USER": os.environ.get("SQL_USER", "user"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

LOGGING = {
    "version": 1,  # Indicates dictConfig format
    "disable_existing_loggers": False,  # Do not disable existing loggers
    # How to format the output
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    # Filter settings
    "filters": {
        # Add filters here if needed
    },
    # Handler settings
    "handlers": {
        "console": {
            "level": os.environ.get("LOG_LEVEL", "INFO"),
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        # You can add file handler here if needed
    },
    # Logger settings
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.environ.get("LOG_LEVEL", "INFO"),  # Log level for Django
            "propagate": True,  # Propagate logs to parent loggers
        },
        "common": {
            "handlers": ["console"],
            "level": os.environ.get("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "meetings": {
            "handlers": ["console"],
            "level": os.environ.get("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "users": {
            "handlers": ["console"],
            "level": os.environ.get("LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}

# Log the allowed hosts
logger.debug(f"Allowed Hosts: {ALLOWED_HOSTS}")

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = False  # In development, True in production if applicable

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "https://*.ngrok.io",
]
CSRF_COOKIE_DOMAIN = ".ngrok.io"
CSRF_COOKIE_SECURE = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
# CORS_ALLOWED_ORIGINS = [
#    "http://localhost:3000",
# ]
CORS_ALLOW_HEADERS = list(default_headers) + [
    "Authorization",
]

# Email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "mailhog")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "1025"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "False") == "True"


# Auth & user model settings
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = os.environ.get("ACCOUNT_EMAIL_VERIFICATION", "none")
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
EMAIL_CONFIRM_REDIRECT_BASE_URL = "http://localhost:8000/email/confirm/"
PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL = (
    "http://localhost:8000/password-reset/confirm/"
)
AUTH_USER_MODEL = "users.CustomUser"
SOCIAL_AUTH_JSONFIELD_ENABLED = True

# Celery settings
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER", "pyamqp://guest@localhost//")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_BACKEND", "redis://127.0.0.1:6379/0")
CELERY_TASK_DEFAULT_QUEUE = "default"
CELERY_TASK_CREATE_MISSING_QUEUES = False
CELERY_TASK_QUEUES = (
    Queue("default"),
    Queue("high_priority"),
    Queue("low_priority"),
)

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
}


def route_task(name, args, kwargs, options, task=None, **kw):
    if ":" in name:
        queue, _ = name.split(":")
        return {"queue": queue}
    return {"queue": "default"}


CELERY_TASK_ROUTES = (route_task,)

# Channels
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.environ.get("CHANNELS_REDIS", "redis://127.0.0.1:6379/0"))],
        },
    },
}

# AllAuth settings
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "key": "",
        },
        "SCOPE": [
            "profile",
            "email",
            "https://www.googleapis.com/auth/calendar",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        "VERIFIED_EMAIL": True,
    },
}
