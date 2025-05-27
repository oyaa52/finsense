# final-pjt/final_pjt_back/product_recommender/apps.py
from django.apps import AppConfig

# product_recommender 앱의 설정을 정의하는 클래스
class ProductRecommenderConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # 기본 자동 필드 타입 설정
    name = "product_recommender"  # 앱 이름
