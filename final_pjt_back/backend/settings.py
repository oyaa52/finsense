import os
from pathlib import Path
import environ
import openai

BASE_DIR = Path(__file__).resolve().parent.parent

# 환경변수 초기화
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

FIN_API_KEY = env("FIN_API_KEY")
KAKAO_API_KEY = env("KAKAO_API_KEY")
KAKAO_REST_API_KEY = env("KAKAO_REST_API_KEY")
YOUTUBE_API_KEY = env("YOUTUBE_API_KEY")
GPT_API_KEY = env("GPT_API_KEY")

# OpenAI API 설정
openai.api_key = GPT_API_KEY

# Build paths inside the project like this: BASE_DIR / 'subdir'.


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-5a+8eibjk_91b(54q!-e&_m*9=p9)(skck%pxf9eghuf_063%2"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    "finsense-cs3c.onrender.com",
]

# Application definition

INSTALLED_APPS = [
    # 사용자 앱
    "accounts",
    "community",
    "products",
    "recommendations",
    "assetinfo",
    "kakaomap",
    "product_recommender",
    # 크롤링 앱
    "market_indices",
    "django_apscheduler",  # 스케줄러 앱 추가
    # 서드파티 앱
    "rest_framework",
    "rest_framework.authtoken",
    "dj_rest_auth",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "dj_rest_auth.registration",
    "corsheaders",
    # 관리자 페이지 디자인 설정
    "jazzmin",
    # 기본 앱
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

SITE_ID = 1

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "https://finsense.seokjae.yeonji.dev",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://finsense.seokjae.yeonji.dev",
    # 필요한 경우 Django 서버 자체의 주소도 추가 (예: 'http://127.0.0.1:8000')
]

ROOT_URLCONF = "backend.urls"

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

CORS_ALLOW_ALL_ORIGINS = True

WSGI_APPLICATION = "backend.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# 정적/미디어
STATIC_URL = "static/"
# STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# 추가된 미디어 설정
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Django REST Framework 설정
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
}

# dj-rest-auth & allauth 설정
# ACCOUNT_USER_MODEL_USERNAME_FIELD = None
# ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_USERNAME_REQUIRED = False
# ACCOUNT_AUTHENTICATION_METHOD = 'email'
# ACCOUNT_EMAIL_VERIFICATION = 'optional'

ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_EMAIL_REQUIRED = False

AUTH_USER_MODEL = "accounts.User"

REST_AUTH = {
    "REGISTER_SERIALIZER": "accounts.serializers.CustomRegisterSerializer",
    "USER_DETAILS_SERIALIZER": "accounts.serializers.CustomUserDetailsSerializer",
}

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

X_FRAME_OPTIONS = "SAMEORIGIN"  # 관리자페이지 같은 출처에서의 임베딩 허용

# Email Settings (Naver SMTP Example)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.naver.com"
EMAIL_PORT = 587  # TLS
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env(
    "NAVER_EMAIL_ID"
)  # 네이버 아이디 (YOUR_NAVER_ID@naver.com 에서 ID 부분)
EMAIL_HOST_PASSWORD = env("NAVER_EMAIL_APP_PASSWORD")  # 네이버 메일 앱 비밀번호
DEFAULT_FROM_EMAIL = f"{env('NAVER_EMAIL_ID')}@naver.com"  # 발신자 이메일 주소

# 캐시 디렉토리 자동 생성
CACHE_DIR = os.path.join(BASE_DIR, "django_cache")
if not os.path.exists(CACHE_DIR):
    try:
        os.makedirs(CACHE_DIR)
        # print(f"캐시 디렉토리 생성됨: {CACHE_DIR}") # 개발 중 확인용. 프로덕션 환경에서는 Django 로깅 시스템 사용 권장.
    except OSError as e:
        print(f"캐시 디렉토리 생성 오류 {CACHE_DIR}: {e}")
        # 선택 사항: 다른 캐시로 대체하거나, 에러를 발생시켜 문제를 알릴 수 있습니다.

# Cache Settings (File-based cache example)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": CACHE_DIR,  # 정의된 CACHE_DIR 사용
        "TIMEOUT": 60 * 60 * 24,  # 24시간
        "OPTIONS": {"MAX_ENTRIES": 1000},
    }
}

# 로깅 설정
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} [{levelname}] {name}: {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "scheduler_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "django_scheduler.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "django_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "django_file"],
            "level": "INFO",
            "propagate": False,
        },
        "market_indices": {
            "handlers": ["console", "scheduler_file"],
            "level": "INFO",
            "propagate": False,
        },
        "apscheduler": {
            "handlers": ["console", "scheduler_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# 로그 디렉토리 생성
LOGS_DIR = BASE_DIR / "logs"
if not LOGS_DIR.exists():
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"로그 디렉토리 생성 오류 {LOGS_DIR}: {e}")

# APPSCHEDULER 설정 (선택적)
# APPSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"
# APPSCHEDULER_RUN_NOW_TIMEOUT = 25
