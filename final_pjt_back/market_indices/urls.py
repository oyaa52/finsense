from django.urls import path
from .views import get_latest_market_indices

app_name = 'market_indices'  # URL 네임스페이스 설정

urlpatterns = [
    # GET /api/market-indices/ - DB에 저장된 최신 KOSPI/KOSDAQ 지수 정보 반환
    path('', get_latest_market_indices, name='latest_market_indices'),
] 