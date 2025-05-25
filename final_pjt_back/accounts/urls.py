from django.urls import path, include
from .views import ProfileDetailAPIView
from rest_framework.routers import DefaultRouter
from .views import FavoriteChannelViewSet, FavoriteVideoViewSet

app_name = "accounts"  # 앱 네임스페이스 설정

router = DefaultRouter()
router.register(r'favorite-channels', FavoriteChannelViewSet, basename='favoritechannel')
router.register(r'favorite-videos', FavoriteVideoViewSet, basename='favoritevideo')

urlpatterns = [
    path("profile/", ProfileDetailAPIView.as_view(), name="profile-detail"),
    path('', include(router.urls)),
    # dj-rest-auth URL들은 프로젝트 레벨의 backend/urls.py에 이미 포함되어 있음
]
