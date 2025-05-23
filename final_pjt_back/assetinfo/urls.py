from django.urls import path
from . import views  # assetinfo 앱 내의 views.py를 임포트합니다.
from .views import AssetPriceListAPIView  # AssetPriceListAPIView 임포트

app_name = "assetinfo"

urlpatterns = [
    # 현물 데이터 제공 API
    path("chart-data/", views.asset_prices_for_chart, name="asset_prices_for_chart"),
    path("prices/", AssetPriceListAPIView.as_view(), name="asset-price-list"),
]
