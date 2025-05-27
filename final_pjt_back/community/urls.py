from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# /posts/ - PostViewSet (게시글 CRUD, 좋아요, 댓글 액션)
router.register('posts', views.PostViewSet, basename='post')
# /follows/ - FollowViewSet (팔로우/언팔로우, 팔로워/팔로잉 목록)
router.register('follows', views.FollowViewSet, basename='follow')

# CommentViewSet은 특정 게시글(post_pk) 하위의 댓글을 다루므로 수동으로 URL 패턴 설정
# 예: /posts/{post_pk}/comments/, /posts/{post_pk}/comments/{comment_pk}/

urlpatterns = [
    path('', include(router.urls)), # ViewSet 라우터 URL 포함
    
    # 특정 게시글의 댓글 목록 조회(GET) 및 댓글 생성(POST)
    # /posts/<post_pk>/comments/
    path('posts/<int:post_pk>/comments/', 
         views.CommentViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='post-comments-list-create'),
    
    # 특정 게시글의 특정 댓글 상세 조회(GET), 수정(PUT/PATCH), 삭제(DELETE)
    # /posts/<post_pk>/comments/<pk>/
    path('posts/<int:post_pk>/comments/<int:pk>/', 
         views.CommentViewSet.as_view({
             'get': 'retrieve', 
             'put': 'update', 
             'patch': 'partial_update', 
             'delete': 'destroy'
         }), 
         name='post-comment-detail'),
] 