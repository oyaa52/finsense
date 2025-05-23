from django.urls import path
from .views import ProfileDetailAPIView

app_name = "accounts"  # 앱 네임스페이스 설정

urlpatterns = [
    path("profile/", ProfileDetailAPIView.as_view(), name="profile-detail"),
    # dj-rest-auth URL들은 프로젝트 레벨의 backend/urls.py에 이미 포함되어 있음
]
