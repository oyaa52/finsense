from django.urls import path
from .views import get_latest_market_indices

app_name = 'market_indices'

urlpatterns = [
    path('', get_latest_market_indices, name='latest_indices'),
] 