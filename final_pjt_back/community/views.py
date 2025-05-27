from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Post, Comment, Follow
from .serializers import (
    PostSerializer,
    CommentSerializer,
    FollowSerializer,
    UserSerializer,
)
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .permissions import IsOwnerOrReadOnly

User = get_user_model()


# 표준 페이지네이션 설정
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # 기본 페이지당 항목 수
    page_size_query_param = "page_size" # 클라이언트가 페이지 크기 변경 시 사용할 쿼리 파라미터
    max_page_size = 100  # 최대 페이지당 항목 수


# 게시글(Post) CRUD 및 '좋아요', '댓글' 액션 ViewSet
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at") # 최신순 정렬
    serializer_class = PostSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        # 액션별 권한 설정
        if self.action in ["list", "retrieve"]: # 목록/상세 조회: 누구나
            return [permissions.AllowAny()]
        elif self.action in ["create", "like", "comment"]: # 생성, 좋아요, 댓글: 인증된 사용자
            return [permissions.IsAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy"]: # 수정/삭제: 소유자만
            return [IsOwnerOrReadOnly()]
        return super().get_permissions()

    def perform_create(self, serializer):
        # 게시글 생성 시 작성자를 현재 로그인 사용자로 설정
        serializer.save(user=self.request.user)

    # 게시글 좋아요/좋아요 취소 액션
    # POST /posts/{pk}/like/
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        if user in post.likes.all(): # 이미 좋아요 한 경우
            post.likes.remove(user) # 좋아요 취소
            liked = False
        else: # 좋아요 하지 않은 경우
            post.likes.add(user) # 좋아요 추가
            liked = True
        return Response(
            {"liked": liked, "likes_count": post.likes.count()},
            status=status.HTTP_200_OK,
        )

    # 게시글 댓글 작성 액션
    # POST /posts/{pk}/comments/
    @action(
        detail=True,
        methods=["post"],
        url_path="comments",
        permission_classes=[IsAuthenticated],
    )
    def comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommentSerializer(
            data=request.data, context={"request": request, "post": post}
        )
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 댓글(Comment) CRUD ViewSet
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by("created_at") # 작성순 정렬
    serializer_class = CommentSerializer
    # permission_classes = [IsAuthenticated, IsOwnerOrReadOnly] # 기본 권한, 아래 get_permissions에서 재정의

    def get_permissions(self):
        # 액션별 권한 설정
        if self.action in ["create"]:
            return [permissions.IsAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsOwnerOrReadOnly()]
        return [permissions.IsAuthenticatedOrReadOnly()] # 목록/상세조회는 인증된 사용자 또는 읽기전용

    def perform_create(self, serializer):
        # 댓글 생성 시 작성자를 현재 로그인 사용자로 설정
        serializer.save(user=self.request.user)


# 팔로우(Follow) 생성/삭제 및 목록 조회 ViewSet
class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated] # 기본 권한: 인증된 사용자

    def get_permissions(self):
        # 액션별 권한 설정 (기본 IsAuthenticated 유지, 필요시 특정 액션에 대해 오버라이드)
        # 예: 특정 사용자 목록 조회 등은 다른 권한을 가질 수 있음
        # if self.action in ["user_followers_list", "user_following_list"]:
        #     return [permissions.AllowAny()] # 예시: 누구나 조회 가능하게 하려면
        return super().get_permissions()

    def get_queryset(self):
        # 현재 로그인 사용자가 팔로우하는 관계만 반환 (기본 목록 조회 시)
        # 이 ViewSet의 기본 GET 요청은 현재 사용자가 팔로워인 Follow 객체들을 나열
        return Follow.objects.filter(follower=self.request.user)

    def perform_create(self, serializer):
        # 팔로우 생성 시 follower를 현재 로그인 사용자로 설정
        # (실제 생성 로직은 아래 create 메소드에서 직접 처리)
        # 이 메소드는 ViewSet의 기본 create 흐름에서는 호출될 수 있으나,
        # 현재 create 메소드를 오버라이드 했으므로 직접 사용되지 않을 수 있음.
        # 만약 직접 사용된다면, following_id는 request.data에서 와야 함.
        try:
            # following_id = request.data.get("following_id") # 이 부분이 필요할 수 있음
            # following_user = User.objects.get(id=following_id)
            # serializer.save(follower=self.request.user, following=following_user)
            serializer.save(follower=self.request.user) # 현재는 follower만 설정
        except serializers.ValidationError as e: # DRF 유효성 검사 오류
            raise e
        except Exception as e: # 기타 예외
            raise serializers.ValidationError(str(e))

    # 현재 로그인 사용자가 팔로우하는 사용자 목록 조회
    # GET /follow/my-following/
    @action(detail=False, methods=["get"], url_path="my-following")
    def my_following_list(self, request):
        following_relations = self.get_queryset() # 사용자가 팔로우하는 관계 (Follow 인스턴스)
        # FollowSerializer는 팔로우 관계 자체를 직렬화 (follower, following 정보 포함)
        serializer = self.get_serializer(following_relations, many=True)
        return Response(serializer.data)

    # 현재 로그인 사용자를 팔로우하는 사용자 목록 조회
    # GET /follow/my-followers/
    @action(detail=False, methods=["get"], url_path="my-followers")
    def my_followers_list(self, request):
        follower_relations = Follow.objects.filter(following=request.user) # 사용자를 팔로우하는 관계 (Follow 인스턴스)
        serializer = self.get_serializer(follower_relations, many=True)
        return Response(serializer.data)

    # 특정 사용자의 팔로워 목록 조회
    # GET /follow/user/{user_pk}/followers/
    @action(
        detail=False, methods=["get"], url_path="user/(?P<user_pk>[^/.]+)/followers"
    )
    def user_followers_list(self, request, user_pk=None):
        user = get_object_or_404(User, pk=user_pk) # 대상 사용자
        followers_relations = Follow.objects.filter(following=user)
        follower_users = [relation.follower for relation in followers_relations] # 팔로워 User 객체 리스트
        # UserSerializer를 사용하여 사용자 정보 직렬화
        serializer = UserSerializer(
            follower_users, many=True, context={"request": request}
        )
        return Response(serializer.data)

    # 특정 사용자가 팔로우하는 사용자 목록 조회
    # GET /follow/user/{user_pk}/following/
    @action(
        detail=False, methods=["get"], url_path="user/(?P<user_pk>[^/.]+)/following"
    )
    def user_following_list(self, request, user_pk=None):
        user = get_object_or_404(User, pk=user_pk) # 대상 사용자
        following_relations = Follow.objects.filter(follower=user)
        followed_users = [relation.following for relation in following_relations] # 팔로잉 User 객체 리스트
        # UserSerializer를 사용하여 사용자 정보 직렬화
        serializer = UserSerializer(
            followed_users, many=True, context={"request": request}
        )
        return Response(serializer.data)

    # 팔로우 생성 (POST /follow/)
    def create(self, request, *args, **kwargs):
        following_id = request.data.get("following_id")
        if not following_id:
            return Response(
                {"detail": "팔로우할 사용자의 ID(following_id)가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            following_user = User.objects.get(id=following_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "팔로우할 사용자를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        follower_user = request.user

        # 자기 자신을 팔로우하는 경우 방지
        if follower_user == following_user:
            return Response(
                {"detail": "자기 자신을 팔로우할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 이미 팔로우 중인 경우 방지
        if Follow.objects.filter(
            follower=follower_user, following=following_user
        ).exists():
            return Response(
                {"detail": "이미 팔로우하고 있는 사용자입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 팔로우 관계 생성
        follow_instance = Follow.objects.create(
            follower=follower_user, following=following_user
        )
        return Response(
            FollowSerializer(follow_instance, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    # 팔로우 해제 (DELETE /follow/{pk}/)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object() # Follow 인스턴스 가져오기
        # 팔로우 관계의 follower가 현재 로그인 사용자가 아니면 권한 없음
        if instance.follower != request.user:
            return Response(
                {
                    "detail": "이 작업을 수행할 권한이 없습니다. 팔로워 본인만 언팔로우할 수 있습니다."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
