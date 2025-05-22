from . import views
from django.urls import path

urlpatterns = [
    path('save_deposit_products/', views.save_deposit_products),
    path('deposit_product_options/<str:fin_prdt_cd>/', views.deposit_product_options),
    path('deposit-products/top-rate/', views.top_rate),
    path('deposit-products/', views.deposit_products)
]
