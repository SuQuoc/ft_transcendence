from datetime import timedelta  # [aguilmea] added manually
import os  # [aguilmea] added manually
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG') == 'True'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # [aguilmea] added manually
    'rest_framework.authtoken',  # [aguilmea] added manually
    'rest_framework_simplejwt.token_blacklist',  # [aguilmea] added manually
    'corsheaders',  # [aguilmea] added manually for cookies
    'core_app',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # [aguilmea] added manually for cookies
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_ACCESS_USER'),
        'PASSWORD': os.environ.get('POSTGRES_ACCESS_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = "core_app.CustomUser"

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# [aguilmea] added manually:
# https://medium.com/django-unleashed/securing-django-rest-apis-with-jwt-authentication-using-simple-jwt-a-step-by-step-guide-28efa84666fe#id_token=eyJhbGciOiJSUzI1NiIsImtpZCI6ImUyNmQ5MTdiMWZlOGRlMTMzODJhYTdjYzlhMWQ2ZTkzMjYyZjMzZTIiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiIyMTYyOTYwMzU4MzQtazFrNnFlMDYwczJ0cDJhMmphbTRsamRjbXMwMHN0dGcuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiIyMTYyOTYwMzU4MzQtazFrNnFlMDYwczJ0cDJhMmphbTRsamRjbXMwMHN0dGcuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTQxNDE4MjQ2NjQ3ODU1MTU1NTQiLCJlbWFpbCI6ImFubmllLmd1aWxtZWF1QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJuYmYiOjE3MjIyNDM0MjQsIm5hbWUiOiJBbm5pZSBHIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0pueFVDQ0s5SThZTi1ieTh5UnVqSkFKWVByYjl6RVhVYmVyQk9xM1h1VzQ3Nm5GQT1zOTYtYyIsImdpdmVuX25hbWUiOiJBbm5pZSIsImZhbWlseV9uYW1lIjoiRyIsImlhdCI6MTcyMjI0MzcyNCwiZXhwIjoxNzIyMjQ3MzI0LCJqdGkiOiJlYWQ1YWMzMWUxZmIzMDdmZjllNTQ3MWJlZDM0NDU4YjhkMjFkOWVkIn0.vsdjq_04QtB_urpSVlsDBoGX01_kCdTGWnER5oh_rruUi9mRq6mMOAOyJFAhJ32WcRJ1ah32eeBlYCo_gm2DSvvAo2OEdclVXdQQy2voYK5-UGLC957akmCBGapJ2pG80GmManTg6F2KcmHFJpY_S-WtV2pQUuS_ccpsGO299IQO0HWqV5eerZBQvfwfd_5CB_TkGjhtK7nqRo6RpP3LcZFQXEARKOSklJQJyS9C54LOYOx1jtUKT2AC3txC5HrIbxRQSqDG7Dsmld6YN6oow_rT5U82AjGzM0olgdOx87H9noa2XZIG8fN0-NNRSdY2fWlLIP_eAUohm0GNOQEi_w
# https://pypi.org/project/django-cors-headers/

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

with open('/run/secrets/private_key.pem', 'r') as f:
    PRIVATE_KEY = f.read()

with open('/run/secrets/public_key.pem', 'r') as f:
    PUBLIC_KEY = f.read()

SIMPLE_JWT = {
    'ALGORITHM': 'RS256',
    'SIGNING_KEY': PRIVATE_KEY,
    'VERIFYING_KEY': PUBLIC_KEY,
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_COOKIE': 'access',  # Cookie name. Enables cookies if value is set.
    'AUTH_COOKIE_DOMAIN': None,  # A string like "example.com", or None for standard domain cookie.
    'AUTH_COOKIE_SECURE': False,  # Whether the auth cookies should be secure (https:// only).
    'AUTH_COOKIE_HTTP_ONLY': True,  # Http only cookie flag.It's not fetch by javascript.
    'AUTH_COOKIE_PATH': '/',  # The path of the auth cookie.
    'AUTH_COOKIE_SAMESITE': 'Lax',  # Whether to set the flag restricting cookie leaks on cross-site requests. This can be 'Lax', 'Strict', or None to disable the flag.
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60), # !!! was added for development, should be 5 minutes (token expiration time)
}

CORS_ALLOWED_ORIGINS = [
    os.environ.get('SERVER_URL'),
]

CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('core_app.authenticate.CustomAuthentication',),
}
# [aguilmea] end of added manually
