from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    # 금융감독원 API 데이터 처리 (데이터베이스 초기 적재 및 업데이트용)
    path(
        "save-deposit-products/",
        views.save_deposit_products,
        name="save_deposit_products",
    ),  # GET: 금감원 API에서 예금 상품 정보를 가져와 DB에 저장/업데이트
    path(
        "save-saving-products/", views.save_saving_products, name="save_saving_products"
    ),  # 금융감독원 API로부터 적금 정보 받아와서 저장
    # 예금 상품 API (클라이언트 조회용)
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
    # 적금 상품 API (클라이언트 조회용)
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
    # 상품 가입 API
    path(
        "deposits/<str:product_code>/subscribe/",
        views.deposit_product_subscribe,
        name="deposit_product_subscribe",
    ),
    path(
        "savings/<str:product_code>/subscribe/",
        views.saving_product_subscribe,
        name="saving_product_subscribe",
    ),
    # 가입한 상품 목록 조회 API
    path(
        "subscriptions/deposits/",
        views.subscribed_deposit_products_list,
        name="subscribed_deposit_products",
    ),
    path(
        "subscriptions/savings/",
        views.subscribed_saving_products_list,
        name="subscribed_saving_products",
    ),
    path(
        "deposits/<str:product_id>/<int:option_id>/subscribe/",
        views.subscribe_deposit,
        name="subscribe_deposit",
    ),
    path(
        "savings/<str:product_id>/<int:option_id>/subscribe/",
        views.subscribe_saving,
        name="subscribe_saving",
    ),
    path("subscriptions/", views.get_user_subscriptions, name="get_user_subscriptions"),
    # 상품 가입 여부 확인 API
    path(
        "deposits/<str:product_code>/is_subscribed/",
        views.check_deposit_subscription_status,
        name="check_deposit_subscription_status",
    ),
    path(
        "savings/<str:product_code>/is_subscribed/",
        views.check_saving_subscription_status,
        name="check_saving_subscription_status",
    ),
]
