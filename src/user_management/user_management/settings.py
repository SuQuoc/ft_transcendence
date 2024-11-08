"""
Django settings for user_management project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from datetime import timedelta
from json import JSONEncoder
import os
from pathlib import Path
from uuid import UUID

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJ_SECRET_KEY")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG") == "True"

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'daphne',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "api",
    "friends",
    "rest_framework",
    "rest_framework_simplejwt",
    'corsheaders',  # [aguilmea] added manually for cookies
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # added for cookies
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "user_management.urls"

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

WSGI_APPLICATION = "user_management.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB"),  # docker-compose environment POSTGRES_DB
        "USER": os.environ.get("POSTGRES_USER") if DEBUG else os.environ.get("POSTGRES_ACCESS_USER"), # i need the postgres root user to run tests, since they are done in a separate database
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD") if DEBUG else os.environ.get("POSTGRES_ACCESS_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),  # docker-compose service name
        "PORT": os.environ.get("DB_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "um/img/"  # had to add um/ before [probably of nginx config] to have the browsable api from DRF to render the page correctly
STATIC_ROOT = os.path.join(BASE_DIR, 'uploads/')
#STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

#TODO: check how we use MEDIA_URL and if it works without debug flag
MEDIA_URL = "um/media/"  # just for the URL in the browser (um/profile_pictures would work) but the folder where the files are is defined in MEDIA_ROOT
MEDIA_ROOT = BASE_DIR / "uploads"


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# SECURITY --------------------------------
CSRF_TRUSTED_ORIGINS = [os.environ.get("SERVER_URL")]


# Security settings for development - clarify if needed !!
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True  # Set to False for local development
# CSRF_COOKIE_SECURE = True  # Set to False for local development

# Allauth settings
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

# REST framework settings
REST_FRAMEWORK = {
    # "DEFAULT_PARSER_CLASSES": [
    #   "rest_framework.parsers.JSONParser",
    # ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'user_management.authenticate.CookieJWTAuthentication',
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}



with open('/run/secrets/public_key.pem', 'r') as f:
    PUBLIC_KEY = f.read()

# https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html?highlight=USER_ID_FIELD#user-id-field
SIMPLE_JWT = {
    'ALGORITHM': 'RS256', # needs to be here for UM to use correct JWT settings, otherwise endpoints will return unauthorized or invalid token
    'VERIFYING_KEY': PUBLIC_KEY, # needs to be here for UM to use correct JWT settings, otherwise endpoints will return unauthorized or invalid token
    # "USER_ID_CLAIM": "user_id",  # just the name of the json key, that others should use to identify the user, could be named to anything u want afaik
}

if DEBUG:
    with open('/run/secrets/private_key.pem', 'r') as f:
        PRIVATE_KEY = f.read()
        SIMPLE_JWT['SIGNING_KEY'] = PRIVATE_KEY # ONLY required for django api tests

CORS_ALLOWED_ORIGINS = [
    os.environ.get('SERVER_URL'),
]

CORS_ALLOW_CREDENTIALS = True

APPEND_SLASH = False


# REDIS ---------------------------------------------------------
REDIS_USER = os.environ.get('REDIS_USER')
REDIS_PASS = os.environ.get('REDIS_PASSWORD')

CHANNEL_LAYERS = {
    #'default': {
    #    'BACKEND': 'channels.layers.InMemoryChannelLayer',  # Use appropriate layer backend
    #},

    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(f"redis://{REDIS_USER}:{REDIS_PASS}@redis:6379/1")],
        },
    },
}