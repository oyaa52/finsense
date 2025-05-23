import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# 환경변수 초기화
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

FIN_API_KEY = env('FIN_API_KEY')
KAKAO_API_KEY = env('KAKAO_API_KEY')
KAKAO_REST_API_KEY = env('KAKAO_REST_API_KEY')

# Build paths inside the project like this: BASE_DIR / 'subdir'.


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-5a+8eibjk_91b(54q!-e&_m*9=p9)(skck%pxf9eghuf_063%2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    # 사용자 앱
    'accounts',
    'community',
    'products',
    'recommendations',
    'assetinfo',
    'kakaomap',
    
    # 서드파티 앱
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth.registration',
    'corsheaders',
    
    # 기본 앱
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

SITE_ID = 1

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware'
]

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5173",
]

ROOT_URLCONF = 'backend.urls'

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

CORS_ALLOW_ALL_ORIGINS = True

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# 정적/미디어
STATIC_URL = 'static/'
# STATICFILES_DIRS = [BASE_DIR / "static"]
# STATIC_ROOT = BASE_DIR / "staticfiles"
# MEDIA_URL = 'media/'
# MEDIA_ROOT = BASE_DIR / "media"

# Django REST Framework 설정
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.IsAuthenticated',
    # ]
}

# dj-rest-auth & allauth 설정
# ACCOUNT_USER_MODEL_USERNAME_FIELD = None
# ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_USERNAME_REQUIRED = False
# ACCOUNT_AUTHENTICATION_METHOD = 'email'
# ACCOUNT_EMAIL_VERIFICATION = 'optional'

ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = False

AUTH_USER_MODEL = 'accounts.User'

REST_AUTH = {
    'REGISTER_SERIALIZER': 'accounts.serializers.CustomRegisterSerializer',
}

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
