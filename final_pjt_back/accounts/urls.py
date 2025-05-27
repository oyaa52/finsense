from django.urls import path, include
from .views import ProfileDetailAPIView, UserProfileDetailAPIView
from rest_framework.routers import DefaultRouter
from .views import FavoriteChannelViewSet, FavoriteVideoViewSet

app_name = "accounts"  # URL 네임스페이스

router = DefaultRouter()
# /api/accounts/favorite-channels/ - 즐겨찾는 채널 CRUD API
router.register(r'favorite-channels', FavoriteChannelViewSet, basename='favoritechannel')
# /api/accounts/favorite-videos/ - 즐겨찾는 비디오 CRUD API
router.register(r'favorite-videos', FavoriteVideoViewSet, basename='favoritevideo')

urlpatterns = [
    # GET, PUT, PATCH /api/accounts/profile/ - 현재 로그인 사용자 프로필 조회/수정
    path("profile/", ProfileDetailAPIView.as_view(), name="profile-detail"),
    # GET /api/accounts/profile/<username>/ - 특정 사용자 프로필 조회
    path("profile/<str:username>/", UserProfileDetailAPIView.as_view(), name="user-profile-detail"),
    path('', include(router.urls)), # ViewSet 라우터 URL 포함
    # dj-rest-auth 관련 URL(로그인, 로그아웃, 회원가입 등)은 backend/urls.py에서 include
]
