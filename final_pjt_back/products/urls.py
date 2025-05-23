from . import views
from django.urls import path

app_name = "products"

urlpatterns = [
    # 예금 상품 정보 저장
    path('save_deposit_products/', views.save_deposit_products),
    # path('deposit_product_options/<str:fin_prdt_cd>/', views.deposit_product_options),
    # path('deposit-products/top-rate/', views.top_rate),
    # path('deposit-products/', views.deposit_products)
    # views.py에 있는 함수들에 대한 경로, 추후 필요할 경우 사용 예정(05/23)
]
