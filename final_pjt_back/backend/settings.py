import os
from pathlib import Path
import environ
import openai
import logging # 로깅 모듈 임포트

# --- 기본 경로 및 환경 변수 설정 ---
BASE_DIR = Path(__file__).resolve().parent.parent

# 로거 인스턴스 생성 (settings.py 자체 로깅용)
logger = logging.getLogger(__name__)

# django-environ을 사용한 .env 파일 로드
env = environ.Env(DEBUG=(bool, False)) # DEBUG 기본값 False
# .env 파일 경로를 명시적으로 지정하여 로드 (BASE_DIR 기준)
env_file_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_file_path):
    environ.Env.read_env(env_file_path)
else:
    logger.warning(f".env 파일을 찾을 수 없습니다: {env_file_path}. 일부 기능이 제한될 수 있습니다.")

# API 키 (환경 변수에서 로드)
FIN_API_KEY = env("FIN_API_KEY", default=None)
KAKAO_API_KEY = env("KAKAO_API_KEY", default=None)
KAKAO_REST_API_KEY = env("KAKAO_REST_API_KEY", default=None)
YOUTUBE_API_KEY = env("YOUTUBE_API_KEY", default=None)
GPT_API_KEY = env("GPT_API_KEY", default=None)

# OpenAI API 키 전역 설정
# 참고: 이 방식은 API 키를 전역적으로 설정합니다. 
# 일반적으로 `OpenAI()` 클라이언트 인스턴스 생성 시 `api_key` 인자로 직접 전달하는 것이 더 안전하고 유연하지만 배포하지 않기에 여기까지.
if GPT_API_KEY:
    openai.api_key = GPT_API_KEY
else:
    logger.warning("GPT_API_KEY가 .env 파일에 설정되지 않았습니다. GPT 관련 기능이 작동하지 않을 수 있습니다.")


# --- 보안 및 배포 관련 설정 ---

SECRET_KEY = env("SECRET_KEY", default="django-insecure-5a+8eibjk_91b(54q!-e&_m*9=p9)(skck%pxf9eghuf_063%2") # 개발용 기본값

# DEBUG: 개발/운영 모드 설정. 운영 환경에서는 반드시 False로 설정
DEBUG = env("DEBUG", default=True) # .env에서 DEBUG 값을 읽어오며, 없으면 True (개발 모드)

# ALLOWED_HOSTS: 서비스할 도메인 및 IP 주소 목록. DEBUG=False일 때 필수 설정.
# 운영 환경에서는 실제 서비스 도메인을 명시
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[]) # .env에서 리스트 형태로 로드, 없으면 빈 리스트


# --- 애플리케이션 정의 ---
INSTALLED_APPS = [
    # 사용자 정의 앱
    "accounts",
    "community",
    "products",
    "recommendations",
    "assetinfo",
    "kakaomap",
    "product_recommender",
    # 크롤링 및 스케줄링 앱
    "market_indices",       # 시장 지수 크롤링
    "django_apscheduler",   # Django 작업 스케줄러
    # 서드파티 인증/API 관련 앱
    "rest_framework",               # Django REST 프레임워크
    "rest_framework.authtoken",   # DRF 토큰 인증
    "dj_rest_auth",               # 사용자 인증 API (로그인, 로그아웃, 비밀번호 재설정 등)
    "allauth",                    # 소셜 로그인 등 다양한 인증 기능 제공
    "allauth.account",            # allauth 계정 관리
    "allauth.socialaccount",      # allauth 소셜 계정 연동
    "dj_rest_auth.registration",  # dj_rest_auth 회원가입 기능
    "corsheaders",                # CORS (Cross-Origin Resource Sharing) 처리
    # 관리자 페이지 디자인
    "jazzmin",                  # Django Admin 테마
    # Django 기본 제공 앱
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

SITE_ID = 1 # allauth 등에서 사용되는 사이트 식별자


# --- 미들웨어 설정 ---
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware", # CORS 헤더 처리 (가장 상단 권장)
    "django.middleware.security.SecurityMiddleware", # 보안 관련 미들웨어
    "django.contrib.sessions.middleware.SessionMiddleware", # 세션 관리
    "django.middleware.common.CommonMiddleware", # 일반적인 HTTP 요청/응답 처리
    "django.middleware.csrf.CsrfViewMiddleware", # CSRF 보호
    "django.contrib.auth.middleware.AuthenticationMiddleware", # 사용자 인증
    "django.contrib.messages.middleware.MessageMiddleware", # 메시지 프레임워크
    "django.middleware.clickjacking.XFrameOptionsMiddleware", # 클릭재킹 방지
    "allauth.account.middleware.AccountMiddleware", # allauth 관련 처리 (예: 자동 로그인)
]


# --- CORS (Cross-Origin Resource Sharing) 설정 ---
# 허용할 프론트엔드 개발 서버 주소 목록
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://127.0.0.1:5173", "http://localhost:5173"])

# CSRF 검증에서 신뢰할 수 있는 출처 (주로 프론트엔드 주소)
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=["http://127.0.0.1:5173", "http://localhost:5173"])

# CORS_ALLOW_ALL_ORIGINS: True로 설정 시 모든 출처에서의 요청을 허용 (CORS_ALLOWED_ORIGINS 무시)
# 개발 환경에서는 편리할 수 있으나, 운영 환경에서는 False로 설정하고 
# CORS_ALLOWED_ORIGINS에 명시된 특정 도메인만 허용하는 것이 보안상 안전
CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", default=True if DEBUG else False)

# CORS_ALLOW_CREDENTIALS: True로 설정 시 쿠키를 포함한 요청 허용 (인증 정보 전달 시 필요)
CORS_ALLOW_CREDENTIALS = True


# --- URL 및 템플릿 설정 ---
ROOT_URLCONF = "backend.urls" # 최상위 URL 설정 파일

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'], # 프로젝트 레벨 템플릿 디렉토리 (필요시)
        "APP_DIRS": True, # 각 앱의 templates 디렉토리 사용
        "OPTIONS": {
            "context_processors": [ # 템플릿 컨텍스트에 기본적으로 전달될 변수/함수
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application" # WSGI 애플리케이션 경로


# --- 데이터베이스 설정 ---
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    "default": env.db_url("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
    # .env 파일에 DATABASE_URL="postgres://user:password@host:port/dbname" 형식으로 설정 가능
}


# --- 비밀번호 검증 설정 ---
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# --- 국제화 설정 ---
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = "ko-kr" # 기본 언어 설정 (한국어)
TIME_ZONE = "Asia/Seoul"    # 시간대 설정 (한국 시간)
USE_I18N = True         # 국제화 기능 활성화
USE_TZ = True           # 시간대 인식 날짜/시간 사용 활성화


# --- 정적 및 미디어 파일 설정 ---
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = "/static/" # 정적 파일 기본 URL
# STATICFILES_DIRS = [BASE_DIR / "static"] # 프로젝트 레벨 정적 파일 디렉토리 (필요시)
STATIC_ROOT = BASE_DIR / "staticfiles" # `collectstatic` 명령으로 수집될 정적 파일들의 루트 디렉토리

MEDIA_URL = "/media/" # 미디어 파일 기본 URL
MEDIA_ROOT = BASE_DIR / "media" # 사용자가 업로드한 미디어 파일들이 저장될 루트 디렉토리


# --- Django REST Framework (DRF) 설정 ---
REST_FRAMEWORK = {
    # API 기본 권한 설정: 모든 요청 허용 (각 View에서 필요에 따라 권한 재정의)
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    # API 기본 인증 방식 설정: 토큰, 세션, 기본 인증 순으로 확인
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",      # 토큰 기반 인증
        "rest_framework.authentication.SessionAuthentication",    # 세션 기반 인증 (브라우저)
        "rest_framework.authentication.BasicAuthentication",      # HTTP 기본 인증 (테스트용)
    ],
}


# --- dj-rest-auth & allauth 설정 ---
# ACCOUNT_USER_MODEL_USERNAME_FIELD: 사용자 모델에서 username 필드 이름 (None이면 username 사용 안 함) - 현재 기본값 None 사용
# ACCOUNT_EMAIL_REQUIRED: 이메일 필수 여부 (True)
# ACCOUNT_USERNAME_REQUIRED: 사용자 이름 필수 여부 (False)
# ACCOUNT_AUTHENTICATION_METHOD: 인증 방식 ('username', 'email', 'username_email') - 현재 'email'
# ACCOUNT_EMAIL_VERIFICATION: 이메일 인증 방식 ('mandatory', 'optional', 'none') - 현재 'optional'

# 현재 프로젝트 설정값 (기존 값 유지 및 주석 보강)
ACCOUNT_EMAIL_VERIFICATION = "none"     # 이메일 인증 사용 안 함
ACCOUNT_AUTHENTICATION_METHOD = "username" # 인증 시 username 사용 (vs 'email', 'username_email')
ACCOUNT_EMAIL_REQUIRED = False          # 회원가입 시 이메일 필수 아님

AUTH_USER_MODEL = "accounts.User"     # 커스텀 사용자 모델 지정 (accounts 앱의 User 모델)

# dj-rest-auth 관련 커스텀 시리얼라이저 설정
REST_AUTH = {
    "REGISTER_SERIALIZER": "accounts.serializers.CustomRegisterSerializer",       # 회원가입 시 사용할 시리얼라이저
    "USER_DETAILS_SERIALIZER": "accounts.serializers.CustomUserDetailsSerializer", # 사용자 정보 조회/수정 시 사용할 시리얼라이저
}


# --- 기본 Primary Key 필드 타입 ---
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField" # 새 앱/모델 생성 시 기본 PK 타입


# --- X-Frame-Options 설정 ---
X_FRAME_OPTIONS = "SAMEORIGIN"  # 관리자 페이지 등 동일 출처에서의 iframe 임베딩 허용


# --- 이메일 발송 설정 (Naver SMTP 예시) ---
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="smtp.naver.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)  # TLS 포트
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True) # TLS 사용 여부
EMAIL_HOST_USER = env("NAVER_EMAIL_ID", default=None) # 네이버 아이디 (예: your_id)
EMAIL_HOST_PASSWORD = env("NAVER_EMAIL_APP_PASSWORD", default=None) # 네이버 메일 앱 비밀번호
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default=f"{EMAIL_HOST_USER}@naver.com" if EMAIL_HOST_USER else None) # 발신자 이메일 주소


# --- 캐시 디렉토리 생성 및 설정 ---
CACHE_DIR = BASE_DIR / "django_cache" # 캐시 파일 저장 디렉토리
if not CACHE_DIR.exists():
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"캐시 디렉토리 생성됨: {CACHE_DIR}")
    except OSError as e:
        logger.error(f"캐시 디렉토리 생성 오류 {CACHE_DIR}: {e}", exc_info=True)

# 파일 기반 캐시 설정
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": str(CACHE_DIR), # 문자열로 변환
        "TIMEOUT": 60 * 60 * 24,  # 기본 타임아웃: 24시간 (초 단위)
        "OPTIONS": {"MAX_ENTRIES": 1000}, # 최대 캐시 항목 수
    }
}


# --- 로깅 설정 ---
# https://docs.djangoproject.com/en/4.2/topics/logging/
LOGS_DIR = BASE_DIR / "logs" # 로그 파일 저장 디렉토리
if not LOGS_DIR.exists(): # 로그 디렉토리 없으면 생성
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"로그 디렉토리 생성됨: {LOGS_DIR}")
    except OSError as e:
        logger.error(f"로그 디렉토리 생성 오류 {LOGS_DIR}: {e}", exc_info=True)

LOGGING = {
    "version": 1, # 로깅 설정 버전
    "disable_existing_loggers": False, # 기존 Django 로거 비활성화 여부 (False 권장)
    
    # 로그 메시지 포맷 정의
    "formatters": {
        "verbose": { # 상세 포맷: 시간 [레벨] 로거이름: 메시지
            "format": "{asctime} [{levelname}] {name}: {message}",
            "style": "{", # {} 스타일 포맷팅 사용
        },
        "simple": { # 간단 포맷: 레벨 메시지
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    
    # 로그 처리기(핸들러) 정의: 로그를 어디에 어떻게 출력할지 결정
    "handlers": {
        "console": { # 콘솔(터미널) 출력 핸들러
            "level": "INFO", # 처리할 최소 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            "class": "logging.StreamHandler", # 콘솔 출력용 클래스
            "formatter": "simple", # 사용할 포맷터 이름
        },
        "scheduler_file": { # 스케줄러 관련 로그 파일 핸들러
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler", # 파일 크기 기반 순환 파일 핸들러
            "filename": LOGS_DIR / "django_scheduler.log", # 로그 파일 경로
            "maxBytes": 1024 * 1024 * 5,  # 로그 파일 최대 크기 (5MB)
            "backupCount": 5, # 보관할 백업 파일 수
            "formatter": "verbose", # 상세 포맷 사용
        },
        "django_file": { # 일반 Django 로그 파일 핸들러
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "django.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    
    # 로거 정의: 특정 이름의 로거가 어떤 핸들러와 레벨을 사용할지 설정
    "loggers": {
        "django": { # Django 프레임워크 내부 로거
            "handlers": ["console", "django_file"], # 콘솔과 django.log 파일에 출력
            "level": "INFO", # INFO 레벨 이상만 처리
            "propagate": False, # 상위 로거(root)로 로그 전파 안 함
        },
        "market_indices": { # market_indices 앱 로거
            "handlers": ["console", "scheduler_file"], # 콘솔과 django_scheduler.log 파일에 출력
            "level": "INFO",
            "propagate": False,
        },
        "apscheduler": { # apscheduler 라이브러리 로거
            "handlers": ["console", "scheduler_file"], # 콘솔과 django_scheduler.log 파일에 출력
            "level": "INFO", 
            "propagate": False,
        },
        # 필요에 따라 다른 앱 또는 모듈에 대한 로거 추가 가능
        # 예: "my_app": { "handlers": ["console", "my_app_file_handler"], "level": "DEBUG", "propagate": False }
    },
}


# --- Jazzmin Admin 테마 설정 (선택적) ---
JAZZMIN_SETTINGS = {
    "site_title": "FinSta 어드민", # 관리자 페이지 좌상단 타이틀
    "site_header": "FinSta 관리",  # 로그인 화면 및 헤더 타이틀
    "site_brand": "FinSta Project", # 관리자 페이지 헤더 브랜드 텍스트
    # "site_logo": "path/to/your/logo.png", # 로고 이미지 경로 (static 파일)
    "welcome_sign": "FinSta 관리자 페이지에 오신 것을 환영합니다.", # 로그인 후 환영 메시지
    "copyright": "FinSta Team", # 푸터 저작권
    "search_model": ["auth.User", "accounts.User"], # 전역 검색에 포함할 모델
    "topmenu_links": [
        {"name": "홈",  "url": "admin:index", "permissions": ["auth.view_user"]},
        # {"model": "auth.User"}, # 특정 모델 바로가기
        # {"app": "products", "name": "상품 관리", "icon": "fas fa-cubes", "models": ("products.DepositProduct", "products.SavingProduct")},
    ],
    "show_sidebar": True, # 사이드바 표시 여부
    "navigation_expanded": True, # 모든 앱 메뉴 기본 펼침 여부
    "icons": { # 앱/모델 아이콘 설정 (Font Awesome 아이콘)
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "accounts.user": "fas fa-user-circle",
        "products.depositproduct": "fas fa-piggy-bank",
        "products.savingproduct": "fas fa-wallet",
        "community.article": "fas fa-comments",
        "community.comment": "fas fa-comment",
        "assetinfo.stockinfo": "fas fa-chart-line",
        "assetinfo.goldinfo": "fas fa-coins",
        "market_indices.marketindex": "fas fa-chart-bar",
        "recommendations.recommendationhistory": "fas fa-history",
    },
    "default_icon_parents": "fas fa-chevron-circle-right", # 기본 부모 아이콘
    "default_icon_children": "fas fa-circle", # 기본 자식 아이콘
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark", # "navbar-light", "navbar-primary", "navbar-secondary", "navbar-dark"
    "accent": "accent-primary",
    "navbar": "navbar-dark navbar-primary", # "navbar-light navbar-white"
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary", # "sidebar-light-primary"
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_ stijl": False,
    "sidebar_flat_style": False,
    "sidebar_legacy_style": False,
    "sidebar_nav_accordion": True,
}
