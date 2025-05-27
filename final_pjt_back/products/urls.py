from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    # 금융감독원 API 데이터 DB 저장/업데이트용 URL
    path(
        "save-deposit-products/",
        views.save_deposit_products,
        name="save_deposit_products",
    ),  # GET: 예금 상품 정보 DB 저장/업데이트
    path(
        "save-saving-products/", views.save_saving_products, name="save_saving_products"
    ),  # GET: 적금 상품 정보 DB 저장/업데이트
    
    # 예금 상품 조회 API URL
    path(
        "deposit-products/",
        views.DepositProductListAPIView.as_view(),
        name="deposit_product_list",
    ),  # GET: 모든 예금 상품 목록 조회 (옵션 포함)
    path(
        "deposit-products/<str:fin_prdt_cd>/",
        views.DepositProductDetailAPIView.as_view(),
        name="deposit_product_detail",
    ),  # GET: 특정 예금 상품 상세 조회 (옵션 포함)
    
    # 적금 상품 조회 API URL
    path(
        "saving-products/",
        views.SavingProductListAPIView.as_view(),
        name="saving_product_list",
    ),  # GET: 모든 적금 상품 목록 조회 (옵션 포함)
    path(
        "saving-products/<str:fin_prdt_cd>/",
        views.SavingProductDetailAPIView.as_view(),
        name="saving_product_detail",
    ),  # GET: 특정 적금 상품 상세 조회 (옵션 포함)
    
    # 상품 가입/해지 API URL
    path(
        "deposits/<str:product_code>/subscribe/",
        views.deposit_product_subscribe,
        name="deposit_product_subscribe",
    ), # POST: 특정 예금 상품 가입/해지
    path(
        "savings/<str:product_code>/subscribe/",
        views.saving_product_subscribe,
        name="saving_product_subscribe",
    ), # POST: 특정 적금 상품 가입/해지
    
    # 가입 상품 조회 API URL
    path(
        "subscriptions/deposits/",
        views.subscribed_deposit_products_list,
        name="subscribed_deposit_products",
    ), # GET: 가입한 모든 예금 상품 목록 조회
    path(
        "subscriptions/savings/",
        views.subscribed_saving_products_list,
        name="subscribed_saving_products",
    ), # GET: 가입한 모든 적금 상품 목록 조회
    
    # 특정 옵션 상품 가입 API URL
    path(
        "deposit/<str:product_id>/<int:option_id>/subscribe/",
        views.subscribe_deposit,
        name="subscribe_deposit",
    ), # POST: 특정 예금 상품의 특정 옵션 가입
    path(
        "saving/<str:product_id>/<int:option_id>/subscribe/",
        views.subscribe_saving,
        name="subscribe_saving",
    ), # POST: 특정 적금 상품의 특정 옵션 가입
    
    # 사용자가 가입한 모든 상품 조회 API URL
    path(
        "subscriptions/", 
        views.get_user_subscriptions, 
        name="get_user_subscriptions"
    ), # GET: 사용자가 가입한 모든 예금/적금 상품 상세 정보 조회
    
    # 상품 가입 여부 확인 API URL
    path(
        "deposits/<str:product_code>/is_subscribed/",
        views.check_deposit_subscription_status,
        name="check_deposit_subscription_status",
    ), # GET: 특정 예금 상품 가입 여부 확인
    path(
        "savings/<str:product_code>/is_subscribed/",
        views.check_saving_subscription_status,
        name="check_saving_subscription_status",
    ), # GET: 특정 적금 상품 가입 여부 확인
]
