from django.urls import path
from .views import asset_prices_for_chart, AssetPriceListAPIView, get_koreaexgold_prices

app_name = 'assetinfo'

urlpatterns = [
    path('chart-prices/', asset_prices_for_chart, name='asset_chart_prices'),
    path('list-prices/', AssetPriceListAPIView.as_view(), name='asset_list_prices'),
    path('koreaexgold-prices/', get_koreaexgold_prices, name='koreaexgold_prices'),
] 