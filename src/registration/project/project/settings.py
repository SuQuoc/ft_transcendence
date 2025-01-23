from datetime import timedelta
import grp, os, pwd, shutil, stat
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_URL = '/static/'
ROOT_URLCONF = 'project.urls'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles/')
if not os.path.exists(STATIC_ROOT):
    os.makedirs(STATIC_ROOT)
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]
for static_dir in STATICFILES_DIRS:
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)


SECRET_KEY = os.environ.get('DJ_SECRET_KEY')
ALLOWED_HOSTS = [os.environ.get('DOMAIN'), 'registration']

DEBUG = os.environ.get('DEBUG') == 'True'
SILK = os.environ.get('SILK') == 'True'
MOCK_EMAIL = os.environ.get('MOCK_EMAIL') == 'True'
MOCK_OTP = os.environ.get('MOCK_OTP') == 'True'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'core_app',
    'django_celery_beat',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REDIS_USER = os.environ.get('REDIS_USER')
REDIS_PASS = os.environ.get('REDIS_PASSWORD')

#values set for testing now
CELERY_BROKER_URL = f"redis://{REDIS_USER}:{REDIS_PASS}@redis_registration:6379/0"
CELERY_RESULT_BACKEND = f"redis://{REDIS_USER}:{REDIS_PASS}@redis_registration:6379/0"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True


if SILK == True:
    SILKY_PYTHON_PROFILER = True
    SILKY_PYTHON_PROFILER_BINARY = True
    MIDDLEWARE.insert(2, 'silk.middleware.SilkyMiddleware')
    INSTALLED_APPS.append('silk')

if DEBUG == True:
    MIDDLEWARE.insert(0, 'core_app.middleware.LogRequestMiddleware')

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

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{REDIS_USER}:{REDIS_PASS}@redis_registration:6379/1",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

WSGI_APPLICATION = 'project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_ACCESS_USER'),
        'PASSWORD': os.environ.get('POSTGRES_ACCESS_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': "5432",
    }
}

AUTH_PASSWORD_VALIDATORS = [
  {
    'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    'OPTIONS': {
      'user_attributes': ('username', 'ft_userid', 'backup_codes'),
      'max_similarity': 0.9,
    }
  },
  {
    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    'OPTIONS': {
      'min_length': 8,
    }
  },
  {
    'NAME': 'core_app.validators.MyMaximumLengthValidator',
    'OPTIONS': {
      'max_length': 120,
    }
  },
  {
    'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
  },
  {
    'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
  }
]

AUTH_USER_MODEL = "core_app.RegistrationUser"

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


with open('/run/secrets/private_key.pem', 'r') as f:
    PRIVATE_KEY = f.read()

with open('/run/secrets/public_key.pem', 'r') as f:
    PUBLIC_KEY = f.read()

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'RS256',
    'SIGNING_KEY': PRIVATE_KEY,
    'VERIFYING_KEY': PUBLIC_KEY,
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken", "rest_framework_simplejwt.tokens.RefreshToken", ),
}

REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'emails/')
if os.path.exists(EMAIL_FILE_PATH):
    shutil.rmtree(EMAIL_FILE_PATH)
if MOCK_EMAIL == True:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    os.makedirs(EMAIL_FILE_PATH)
#    celery_user = 'celeryuser'
#    uid = pwd.getpwnam(celery_user).pw_uid
#    gid = grp.getgrnam(celery_user).gr_gid
#    os.chown(EMAIL_FILE_PATH, uid, gid)
#    os.chmod(EMAIL_FILE_PATH, stat.S_IRWXU | stat.S_IRWXG)
    os.chmod(EMAIL_FILE_PATH, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
PASSWORD_RESET_TIMEOUT = 600

CORS_ALLOWED_ORIGINS = [
    "https://api.intra.42.fr",
]
APPEND_SLASH=False # [aguilmea] changed temporarly

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
]
if DEBUG == True:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
     "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "WARNING",
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'WARNING',  # Set the logging level for Django-specific messages
                'propagate': True,
            },
            'celery': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': True,
            }
        },
    }

CSRF_TRUSTED_ORIGINS = [os.environ.get("SERVER_URL")] # [aguilmea] added for admin login

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "non_verified_users_after_one_day": {
        "task": "project.celery.non_verified_users_after_one_day",
        #"schedule": crontab(minute="*/1"), # for testing purpose
        "schedule": crontab(minute=0, hour=0),
    },
    "users_without_login_within_one_year": {
        "task": "project.celery.users_without_login_within_one_year",
        #"schedule": crontab(minute="*/1"), # for testing purpose
        "schedule": crontab(minute=0, hour=0),
    },
}

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

CELERY_IMPORTS = ("core_app.tasks",)
