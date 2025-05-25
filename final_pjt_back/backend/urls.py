from django.contrib import admin
from django.urls import path, include
from django.conf import settings # 설정 파일을 가져오기 위해 추가
from django.conf.urls.static import static # static 파일 관련 함수 추가

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dj-rest-auth/", include("dj_rest_auth.urls")),
    path("dj-rest-auth/registration/", include("dj_rest_auth.registration.urls")),
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/community/", include("community.urls")),
    path("api/v1/products/", include("products.urls")),
    path("api/v1/recommendations/", include("recommendations.urls")),
    path("api/v1/assetinfo/", include("assetinfo.urls")),
    path("api/v1/kakaomap/", include("kakaomap.urls")),
]

# 개발 환경에서 미디어 파일을 서빙하기 위한 설정 추가
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
