from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('posts', views.PostViewSet, basename='post')
router.register('follows', views.FollowViewSet, basename='follow')
# CommentViewSet도 router에 등록하거나, 현재 수동 URL 설정을 유지할 수 있습니다.
# 프론트엔드에서 posts/post_pk/comments/comment_pk/ 형태를 사용하므로 현재 수동 설정이 유효합니다.
# router.register(r'posts/(?P<post_pk>\d+)/comments', views.CommentViewSet, basename='post-comments') # DRF-Nested-Routers 예시

urlpatterns = [
    path('', include(router.urls)),
    # 아래 두 URL 패턴은 CommentViewSet을 사용합니다.
    # GET, POST to /posts/<post_pk>/comments/
    path('posts/<int:post_pk>/comments/', views.CommentViewSet.as_view({'get': 'list', 'post': 'create'}), name='post-comments-list-create'),
    # GET, PUT, PATCH, DELETE to /posts/<post_pk>/comments/<pk>/
    path('posts/<int:post_pk>/comments/<int:pk>/', views.CommentViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update', 
        'patch': 'partial_update', 
        'delete': 'destroy'
    }), name='post-comment-detail'),
    # path('posts/<int:post_id>/comments/', views.CommentListCreateAPIView.as_view(), name='comment-list-create'), # 주석 처리 또는 삭제
] 