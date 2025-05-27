from django.contrib import admin
from django.urls import path, include
from django.conf import settings       # Django 설정 임포트
from django.conf.urls.static import static # 정적/미디어 파일 서빙 헬퍼

# 프로젝트의 최상위 URL 패턴 정의
urlpatterns = [
    # Django 관리자 페이지
    path("admin/", admin.site.urls, name="admin"),
    
    # dj-rest-auth 기본 URL (로그인, 로그아웃, 비밀번호 재설정 등)
    path("dj-rest-auth/", include("dj_rest_auth.urls")),
    # dj-rest-auth 회원가입 관련 URL
    path("dj-rest-auth/registration/", include("dj_rest_auth.registration.urls")),
    
    # --- API 엔드포인트 (버전 v1) ---
    # accounts 앱 API URL
    path("api/v1/accounts/", include("accounts.urls")),
    # community 앱 API URL
    path("api/v1/community/", include("community.urls")),
    # products 앱 API URL
    path("api/v1/products/", include("products.urls")),
    # recommendations 앱 API URL (YouTube 영상 추천)
    path("api/v1/recommendations/", include("recommendations.urls")),
    # product_recommender 앱 API URL (금융 상품 추천)
    path("api/v1/product-recommender/", include("product_recommender.urls")),
    # assetinfo 앱 API URL (주식, 금 정보)
    path("api/v1/assetinfo/", include("assetinfo.urls")),
    # kakaomap 앱 API URL (은행/증권사 지도 검색)
    path("api/v1/kakaomap/", include("kakaomap.urls")),
    # market_indices 앱 API URL (코스피/코스닥 지수)
    path("api/v1/market-indices/", include("market_indices.urls")),
]

# 개발 환경(DEBUG=True)에서 사용자가 업로드한 미디어 파일을 Django 개발 서버를 통해 서빙하기 위한 설정.
# 운영 환경에서는 웹 서버(예: Nginx)가 직접 미디어 파일을 서빙하도록 설정해야 합니다.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
