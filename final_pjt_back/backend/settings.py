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
DEBUG = True

ALLOWED_HOSTS = []


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
    "django.contrib.sites",
    # 각 소셜 프로바이더 추가
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.kakao",
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
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # 필요한 경우 Django 서버 자체의 주소도 추가 (예: 'http://127.0.0.1:8000')
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # 아래 두 줄은 ModuleNotFoundError를 유발하므로 제거 또는 주석 처리
                # "allauth.account.context_processors.account",
                # "allauth.socialaccount.context_processors.socialaccount",
            ],
        },
    },
]

# CORS_ALLOW_ALL_ORIGINS = True

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

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

# 로그인이 필요한 경우 리디렉션될 로그인 페이지 URL
LOGIN_URL = '/accounts/login/'

# Allauth 설정 (필요에 따라 커스터마이징)
ACCOUNT_AUTHENTICATION_METHOD = 'email' # 이메일 또는 (username + 이메일)로 로그인
ACCOUNT_EMAIL_REQUIRED = True          # 이메일 필드를 필수로 설정
ACCOUNT_USERNAME_REQUIRED = True       # User 모델에 username이 있으므로 True로 설정.
                                       # 소셜 로그인 시 username은 이메일 등으로 자동 생성되거나,
                                       # adapter를 통해 커스터마이징 가능.
ACCOUNT_EMAIL_VERIFICATION = 'optional'# 이메일 인증은 선택적으로. (소셜은 이미 인증된 경우가 많음)
                                       # 'none'으로 하면 인증 메일 발송 안 함.

# LOGIN_REDIRECT_URL = '/'               # 로그인 후 리디렉션될 URL. Vue 앱의 콜백 핸들러로 변경.
LOGIN_REDIRECT_URL = 'http://localhost:5173/social-callback' # Vue 앱의 소셜 로그인 콜백 처리 경로
LOGOUT_REDIRECT_URL = '/'              # 로그아웃 후 리디렉션될 URL (추가 권장)
ACCOUNT_LOGOUT_ON_GET = True           # GET 요청으로 로그아웃 처리 (편의성)

# 이메일 중복 허용 안 함 (User 모델에 email unique=True 이므로 필수)
ACCOUNT_UNIQUE_EMAIL = True

# 소셜 계정으로 가입 시 추가 정보 입력 없이 자동 가입 (필요에 따라 False로 변경 후 폼 제공)
SOCIALACCOUNT_AUTO_SIGNUP = True

# 소셜 계정 관련 설정
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the client secrets
        # or list them here:
        # 'APP': {  # 주석 처리 또는 삭제
            # 'client_id': 'YOUR_GOOGLE_CLIENT_ID',
            # 'secret': 'YOUR_GOOGLE_CLIENT_SECRET',
            # 'key': ''
        # },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'kakao': {
        # 'APP': {  # 주석 처리 또는 삭제
            # 'client_id': 'YOUR_KAKAO_NATIVE_APP_KEY_OR_REST_API_KEY',
            # 'secret': 'YOUR_KAKAO_CLIENT_SECRET',
        # },
        'SCOPE': [
            'profile_nickname',
            'profile_image',
            # 'account_email', # 이메일 스코프 제거
        ],
        # 'AUTH_PARAMS': {'auth_type': 'reauthenticate'}, # 필요시
    }
}

# 기존 settings.py 파일의 맨 아래에 추가합니다.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'allauth': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

SESSION_COOKIE_SAMESITE = 'Lax' # SameSite 설정 추가

# Custom Adapters
ACCOUNT_ADAPTER = 'accounts.adapter.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'accounts.adapter.CustomSocialAccountAdapter'

