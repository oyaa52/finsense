from . import views
from django.urls import path

app_name = "kakaomap"  # URL 네임스페이스 설정

urlpatterns = [
    # GET /api/kakaomap/apikey/ - 카카오맵 JavaScript API 키 및 REST API 키 반환
    path('get_kakao_map_api_key/', views.get_kakao_map_api_key, name='get_kakao_map_api_keys'),
]