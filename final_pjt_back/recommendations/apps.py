# final-pjt/final_pjt_back/recommendations/apps.py
from django.apps import AppConfig

# recommendations 앱의 설정을 정의하는 클래스
class RecommendationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # 기본 자동 필드 타입 설정
    name = "recommendations"  # 앱 이름
