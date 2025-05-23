from . import views
from django.urls import path

app_name = "kakaomap"

urlpatterns = [
    # 카카오 맵 API 키 반환
    path('get_kakao_map_api_key/', views.get_kakao_map_api_key),
]