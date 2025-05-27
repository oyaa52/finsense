from django.urls import path
from .views import asset_prices_for_chart, AssetPriceListAPIView, get_koreaexgold_prices

app_name = 'assetinfo'  # URL 네임스페이스 설정

urlpatterns = [
    # GET /api/assetinfo/chart-prices/?asset_name=<asset_name> - 특정 자산 가격 정보 (차트용)
    path('chart-prices/', asset_prices_for_chart, name='asset_chart_prices'),
    
    # GET /api/assetinfo/list-prices/?asset_name=<name>&start_date=<date>&end_date=<date> - 자산 가격 목록 (필터링 가능)
    path('list-prices/', AssetPriceListAPIView.as_view(), name='asset_list_prices'),
    
    # GET /api/assetinfo/koreaexgold-prices/?type=<type>&from=<date>&to=<date> - 한국금거래소 금/은 시세 (차트용)
    path('koreaexgold-prices/', get_koreaexgold_prices, name='koreaexgold_prices'),
] 