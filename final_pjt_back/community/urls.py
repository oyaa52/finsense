from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('posts', views.PostViewSet, basename='post')
router.register('follows', views.FollowViewSet, basename='follow')

urlpatterns = [
    path('', include(router.urls)),
    path('posts/<int:post_pk>/comments/', views.CommentViewSet.as_view({'get': 'list', 'post': 'create'}), name='post-comments'),
    path('posts/<int:post_pk>/comments/<int:pk>/', views.CommentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='post-comment-detail'),
] 