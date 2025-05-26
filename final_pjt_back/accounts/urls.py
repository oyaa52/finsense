from django.urls import path, include
from .views import (
    ProfileDetailAPIView, 
    UserProfileDetailAPIView, 
    FavoriteChannelViewSet, 
    FavoriteVideoViewSet,
    GetTokenByOTTView,
)
from rest_framework.routers import DefaultRouter

app_name = "accounts"  # 앱 네임스페이스 설정

router = DefaultRouter()
router.register(r'favorite-channels', FavoriteChannelViewSet, basename='favoritechannel')
router.register(r'favorite-videos', FavoriteVideoViewSet, basename='favoritevideo')

urlpatterns = [
    path('', include(router.urls)),
    path('exchange-onetime-token/', GetTokenByOTTView.as_view(), name='exchange_onetime_token'),
    path('profile/', ProfileDetailAPIView.as_view(), name="profile-detail"),
    path("profile/<str:username>/", UserProfileDetailAPIView.as_view(), name="user-profile-detail"),
    path('favorite-channels/', FavoriteChannelViewSet.as_view({'get': 'list', 'post': 'create'}), name='favorite_channel_list'),
    path('favorite-channels/<int:pk>/', FavoriteChannelViewSet.as_view({'delete': 'destroy'}), name='favorite_channel_detail'),
    path('favorite-channels/is_favorite/', FavoriteChannelViewSet.as_view({'get': 'is_favorite'}), name='favorite_channel_is_favorite'),
    path('favorite-videos/', FavoriteVideoViewSet.as_view({'get': 'list', 'post': 'create'}), name='favorite_video_list'),
    path('favorite-videos/<int:pk>/', FavoriteVideoViewSet.as_view({'delete': 'destroy'}), name='favorite_video_detail'),
    path('favorite-videos/is_favorite/', FavoriteVideoViewSet.as_view({'get': 'is_favorite'}), name='favorite_video_is_favorite'),
]
