#06.01
#vscode에는 현재 베포 서버용 settings가 설정되어 있음
#github애는 현재 개발 서버용 settings가 설정되어 있음
import os
from pathlib import Path
from datetime import timedelta
import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from config.logger import CustomisedJSONFormatter
import dj_database_url

#로컬서버에서의 cors, csrftoken  설정
#momo@gmail.com-momo : debug=True
#test develop
env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")

#prod mode
# ALLOWED_HOSTS = [
#     "127.0.0.1",
#     "localhost",
#     "backend.petmo.monster",
#     "frontend.petmo.monster", 
#     "petmo.monster"
# ]
ALLOWED_HOSTS=["*"]

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)




#CORS Setting
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS=True
CORS_ORIGIN_ALLOW = True
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:3000", 
    "http://localhost:3000", 
    "https://petmo-frontend-4tqxc2n8y-moonyerim2.vercel.app",
    "https://frontend.petmo.monster"
    
]

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://petmo-frontend-4tqxc2n8y-moonyerim2.vercel.app", # : "front-address"
    "https://frontend.petmo.monster"
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'X-CSRFToken'
    'x-requested-with',
    'Set-Cookie',
]
ACCOUNT_PASSWORD_INPUT_RENDER_VALUE = True  
ACCOUNT_SESSION_REMEMBER = True  
SESSION_COOKIE_AGE = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

AUTH_COOKIE_DOMAIN=".on.render.com"
CSRF_COOKIE_SECURE=False
AUTH_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "Lax"



THIRD_PARTY_APPS=[
    # "rest_framework_simplejwt.token_blacklist",
    # "dj_rest_auth",
    # "dj_rest_auth.registration",
    'rest_framework',
    # "rest_framework.authtoken",
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    'django_seed',
    'whitenoise.runserver_nostatic',
    'debug_toolbar',
    
]
CUSTOM_APPS=[
    "users.apps.UsersConfig",
    "pets.apps.PetsConfig",
    "categories.apps.CategoriesConfig",
    "posts.apps.PostsConfig",
    "common.apps.CommonConfig",
    "images.apps.ImagesConfig",
    "auths.apps.AuthsConfig",
    "bookmarks.apps.BookmarksConfig",
    "likes.apps.LikesConfig",
]

SYSTEM_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

]
SITE_ID = 1

INSTALLED_APPS = SYSTEM_APPS + THIRD_PARTY_APPS + CUSTOM_APPS

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

DEBUG = 'RENDER' not in os.environ
# DEBUG=True

if DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, 'app','static')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    DATABASES = {
        'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR/ 'db.sqlite3',
            }
    }
else:
     DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
        )
                    
    }
     
if not DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, 'app','static')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

#debug tool-bar        
INTERNAL_IPS=[
    '127.0.0.1',
]

REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES':(
        # 'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 10,
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

APP_ID = 'petmo_elk'
#ELK-Logstash
# LOGGING={
#     "version":1,
#         'disable_existing_loggers': False,
#     'formatters': {
#         'simple': {
#             'format': '[%(asctime)s] %(levelname)s|%(name)s|%(message)s',
#             'datefmt': '%Y-%m-%d %H:%M:%S',
#         },
#         "json": {
#             '()': CustomisedJSONFormatter,
#         },
#     },
#     'handlers': {
#         'app_log_file': {
#             'level': 'DEBUG',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'filename': Path(BASE_DIR).resolve().joinpath('app/logs', 'app.log'),
#             'maxBytes': 1024 * 1024 * 15,  # 15MB
#             'backupCount': 10,
#             'formatter': 'json',
#         },
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'simple'
#         }
#     },
#     'root': {
#         'handlers': ['console', 'app_log_file'],
#         'level': 'DEBUG',
#     }
# }
# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

#by gunicorn
STATIC_URL = '/static/'

#elasticssearch
ELASTICSEARCH_DSL = {
    'default': {
        "hosts": "localhost:9200"
    }
}

MEDIA_ROOT = "uploads"

MEDIA_URL = "user-uploads/"
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = "users.User"

#External API KEY
KAKAO_API_KEY=env("KAKAO_API_KEY")
IP_GEOAPI=env("IP_GEOAPI")
#Cloudflare
CF_TOKEN=env("CF_TOKEN")
CF_ID=env("CF_ID")

#Sentry -> log monitoring
if not DEBUG:#개발 환경에서는 작동 안함
    
    sentry_sdk.init(
        dsn="https://e7a874aa712847f1a0659474973d022e@o4505280354975744.ingest.sentry.io/4505280371032064",
        integrations=[
            DjangoIntegration(),
        ],
        traces_sample_rate=1.0,
        send_default_pii=True
    )
