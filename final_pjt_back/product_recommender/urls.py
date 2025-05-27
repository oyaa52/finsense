# final-pjt/final_pjt_back/product_recommender/urls.py
from django.urls import path
from . import views # 현재 앱(product_recommender)의 views 모듈 임포트

app_name = 'product_recommender'  # URL 네임스페이스 설정 (예: {% url 'product_recommender:get_gpt_recommendations' %})

urlpatterns = [
    # GET (사용 중단) /api/recommender/recommendations/ - 사용자 프로필 기반 금융상품 추천 (현재 사용 중단 안내)
    path('recommendations/', views.get_recommendations, name='get_recommendations'),
    
    # POST /api/recommender/gpt/ - GPT-4o 모델 기반 금융상품 추천
    path('gpt/', views.get_gpt_recommendations, name='get_gpt_recommendations'),
    
    # POST /api/recommender/generate-image/ - DALL-E 3 모델 기반 이미지 생성 및 저장
    path('generate-image/', views.generate_image, name='generate_image'),
] 