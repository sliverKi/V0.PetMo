import os, my_DB, prod_DB
from pathlib import Path
from datetime import timedelta
import environ
# import dj_database_url
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection
#로컬서버에서의 cors, csrftoken  설정
#momo@gmail.com-momo : debug=True

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



#CORS Setting
CORS_ALLOW_CREDENTIALS = True
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

AUTH_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_HTTPONLY = False

CCOUNT_PASSWORD_INPUT_RENDER_VALUE = True  
ACCOUNT_SESSION_REMEMBER = True  
SESSION_COOKIE_AGE = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

THIRD_PARTY_APPS=[
    #JWT
    # "rest_framework_simplejwt.token_blacklist",
    # "dj_rest_auth",
    # "dj_rest_auth.registration",
    # "rest_framework.authtoken",
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    'django_seed',
    'django_elasticsearch_dsl',
    'django_elasticsearch_dsl_drf',
    'whitenoise.runserver_nostatic',
    'debug_toolbar',
    'storages',
    # 'silk'
]
CUSTOM_APPS=[
    "auths.apps.AuthsConfig",
    "addresses.apps.AddressesConfig",
    "users.apps.UsersConfig",
    "petCategories.apps.petCategoriesConfig",
    "boardCategories.apps.boardCategoriesConfig",
    "posts.apps.PostsConfig",
    "common.apps.CommonConfig",
    "bookmarks.apps.BookmarksConfig",
    "likes.apps.LikesConfig",
    "search.apps.SearchConfig",
    "history.apps.HistoryConfig",
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
    # 'silk.middleware.SilkyMiddleware',
    #'config.search.searchRateLimiterMiddleware',# 검색어 관리 및 검색 횟수 제한 미들웨어 추가 ~> 모든 페이지에 적용되는 문제 발생 ~> 특정 url에만 적용하기 위해 옮김
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

# DEBUG = 'RENDER' not in os.environ
# DEBUG=env("DEBUG")
DEBUG=True

     
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

ELASTICSEARCH_DSL = {
    'default': {
        "hosts": "elasticsearch:9200"
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

DEFAULT_CHARSET = 'utf-8'
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

#by gunicorn
# STATIC_URL = '/static/'



MEDIA_ROOT = "uploads"

MEDIA_URL = "user-uploads/"
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = "users.User"

#External API KEY
KAKAO_API_KEY=env("KAKAO_API_KEY")
IP_GEOAPI=env("IP_GEOAPI")

#CloudFlare->delete
CF_TOKEN=env("CF_TOKEN")
CF_ID=env("CF_ID")

#S3
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_S3_SECURE_URLS = False       # use http instead of https
AWS_QUERYSTRING_AUTH = False     # don't add complex authentication-related query parameters for requests

AWS_S3_ACCESS_KEY_ID = env("AWS_S3_ACCESS_KEY_ID")
AWS_S3_SECRET_ACCESS_KEY = env("AWS_S3_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")

STATIC_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME

#Redis(elasticCache)
REDIS_PORT = env("REDIS_PORT")
# REDIS_HOST = env("REDIS_HOST")
REDIS_HOST='localhost'
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
    
#DB

RDS_PASSWORD=env('RDS_PASSWORD')
RDS_HOSTNAME=env('RDS_HOSTNAME')
RDS_POST=env('RDS_PORT')

if DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, 'app','static')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    DATABASES = my_DB.DATABASES

else:
    DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'petmoRDS',
        'USER': 'admin',
        'PASSWORD': 'admin1234',
        'HOST': 'petmo.ck09gu2by087.ap-northeast-2.rds.amazonaws.com',  # 예: 'your-db-instance.rds.amazonaws.com'
        'PORT': 3306,
        }
    }
    
#elasticssearch & OpenSearch
AWS_ACCESS_KEY_ID=env("AWS_S3_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY=env("AWS_S3_SECRET_ACCESS_KEY")
AWS_REGION=env("AWS_S3_REGION_NAME")
SERVICE=env("SERVICE")

awsauth = AWS4Auth(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, SERVICE)
OPENSEARCH_HOST=env("OPENSEARCH_HOST")
if DEBUG:
    ELASTICSEARCH_DSL = {
        'default': {
            "hosts": "localhost:9200"
        }
    }
else:
    ELASTICSEARCH_DSL = {
       'default': {
        'hosts': OPENSEARCH_HOST,
        'http_auth': awsauth,
        'use_ssl': True,
        'verify_certs': True,
        'connection_class': RequestsHttpConnection
        },
    }

#콘솔창에서 SQL 쿼리 보기
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}
